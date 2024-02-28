from wsgiref import headers
import pytest
import json
from string import Template

from testsuite.databases import pgsql


# Start the tests via `make test-debug` or `make test-release`


'''
async def test_first_time_users(service_client):
    response = await service_client.post(
        '/v1/hello',
        params={'name': 'userver'},
    )
    assert response.status == 200
    assert response.text == 'Hello, userver!\n'


async def test_db_updates(service_client):
    response = await service_client.post('/v1/hello', params={'name': 'World'})
    assert response.status == 200
    assert response.text == 'Hello, World!\n'

    response = await service_client.post('/v1/hello', params={'name': 'World'})
    assert response.status == 200
    assert response.text == 'Hi again, World!\n'

    response = await service_client.post('/v1/hello', params={'name': 'World'})
    assert response.status == 200
    assert response.text == 'Hi again, World!\n'


@pytest.mark.pgsql('db_1', files=['initial_data.sql'])
async def test_db_initial_data(service_client):
    response = await service_client.post(
        '/v1/hello',
        params={'name': 'user-from-initial_data.sql'},
    )
    assert response.status == 200
    assert response.text == 'Hi again, user-from-initial_data.sql!\n'
'''


@pytest.mark.pgsql('db_1', files=['initial_data.sql'])
async def test_db_initial_data(service_client):
    response = await service_client.get(
        '/v1/employee/info',
        params={'employee_id': 'first_id'},
        headers={'Authorization': 'Bearer first_token'},
    )

    assert response.status == 200
    assert response.text == ('{"id":"first_id","name":"First",'
                             '"phones":[],"surname":"A"}')


@pytest.mark.pgsql('db_1', files=['initial_data.sql'])
async def test_employees(service_client):
    response = await service_client.post(
        '/v1/employee/add-head',
        params={'employee_id': 'second_id'},
        headers={'Authorization': 'Bearer first_token'},
        json={'head_id': 'first_id'},
    )

    assert response.status == 200

    response = await service_client.get(
        '/v1/employees',
        headers={'Authorization': 'Bearer first_token'},
    )

    assert response.status == 200
    assert response.text == ('{"employees":[{"id":"second_id"'
                             ',"name":"Second","surname":"B"}]}')


@pytest.mark.pgsql('db_1', files=['initial_data.sql'])
async def test_add_head(service_client):
    response = await service_client.post(
        '/v1/employee/add-head',
        params={'employee_id': 'second_id'},
        headers={'Authorization': 'Bearer first_token'},
        json={'head_id': 'first_id'},
    )

    assert response.status == 200

    response = await service_client.get(
        '/v1/employee/info',
        params={'employee_id': 'second_id'},
        headers={'Authorization': 'Bearer first_token'},
    )

    assert response.status == 200

    response_body = response.text
    head_id = json.loads(response_body)['head_id']

    assert head_id == 'first_id'


@pytest.mark.pgsql('db_1', files=['initial_data.sql'])
async def test_add(service_client):
    response = await service_client.post(
        '/v1/employee/add',
        headers={'Authorization': 'Bearer first_token'},
        json={'name': 'Third', 'surname': 'C', 'role': 'user'},
    )

    assert response.status == 200
    new_id = json.loads(response.text)['login']
    new_password = json.loads(response.text)['password']

    response = await service_client.get(
        '/v1/employee/info',
        params={'employee_id': new_id},
        headers={'Authorization': 'Bearer first_token'},
    )

    assert response.status == 200
    assert response.text == ('{"id":"' + new_id + '","name":"Third",'
                             '"password":"' + new_password + '",'
                             '"phones":[],"surname":"C"}')


@pytest.mark.pgsql('db_1', files=['initial_data.sql'])
async def test_remove(service_client):
    response = await service_client.post(
        '/v1/employee/remove',
        params={'employee_id': 'second_id'},
        headers={'Authorization': 'Bearer first_token'},
        json={'name': 'Third', 'surname': 'C', 'role': 'user'},
    )

    assert response.status == 200

    response = await service_client.get(
        '/v1/employee/info',
        params={'employee_id': 'second_id'},
        headers={'Authorization': 'Bearer first_token'},
    )

    assert response.status != 200


@pytest.mark.pgsql('db_1', files=['initial_data.sql'])
async def test_edit(service_client):
    response = await service_client.post(
        '/v1/profile/edit',
        headers={'Authorization': 'Bearer second_token'},
        json={'phones': ['+7999999999']},
    )

    assert response.status == 200

    response = await service_client.get(
        '/v1/employee/info',
        params={'employee_id': 'second_id'},
        headers={'Authorization': 'Bearer first_token'},
    )

    assert response.status == 200

    response_body = response.text
    phones = json.loads(response_body)['phones']

    assert phones == ['+7999999999']

    response = await service_client.post(
        '/v1/profile/edit',
        headers={'Authorization': 'Bearer second_token'},
        json={'email': 'second@mail.com'},
    )

    assert response.status == 200

    response = await service_client.get(
        '/v1/employee/info',
        params={'employee_id': 'second_id'},
        headers={'Authorization': 'Bearer first_token'},
    )

    assert response.status == 200

    response_body = response.text
    email = json.loads(response_body)['email']

    assert email == 'second@mail.com'


@pytest.mark.pgsql('db_1', files=['initial_data.sql'])
async def test_authorize(service_client):
    response = await service_client.post(
        '/v1/profile/edit',
        headers={'Authorization': 'Bearer first_token'},
        json={'password': 'first_password'},
    )

    assert response.status == 200

    response = await service_client.post(
        '/v1/authorize',
        json={'login': 'first_id', 'password': 'first_password'},
    )

    assert response.status == 200

    # Wrong password
    response = await service_client.post(
        '/v1/authorize',
        json={'login': 'first_id', 'password': 'wrong_password'},
    )

    assert response.status == 404

    # Wrong token
    response = await service_client.get(
        '/v1/employee/info',
        params={'employee_id': 'first_id'},
        headers={'Authorization': 'Bearer wrong_token'},
    )

    assert response.status == 403

    # Authorization header without Bearer
    response = await service_client.get(
        '/v1/employee/info',
        params={'employee_id': 'first_id'},
        headers={'Authorization': 'first_token'},
    )

    assert response.status == 401

    # No authorization header
    response = await service_client.get(
        '/v1/employee/info',
        params={'employee_id': 'first_id'},
    )

    assert response.status == 401

    # No admin rights
    response = await service_client.post(
        '/v1/employee/add',
        headers={'Authorization': 'Bearer second_token'},
        json={'name': 'Third', 'surname': 'C', 'role': 'user'},
    )

    assert response.status == 403


@pytest.mark.pgsql('db_1', files=['initial_data.sql'])
async def test_search_add(service_client):
    response = await service_client.post(
        '/v1/employee/add',
        headers={'Authorization': 'Bearer first_token'},
        json={'name': 'Fourth', 'surname': 'D', 'role': 'user'},
    )

    assert response.status == 200
    new_id = json.loads(response.text)['login']
    new_password = json.loads(response.text)['password']

    response = await service_client.get(
        '/v1/search/intersect',
        json={'search_keys': ['Fourth'], 'limit': 1},
        headers={'Authorization': 'Bearer first_token'},
    )

    assert response.status == 200
    response_required = Template('{"employees":[{"id":"${id}",'
                                 '"name":"Fourth","surname":"D"}]}')
    assert response.text == (response_required.substitute(id=new_id))


@pytest.mark.pgsql('db_1', files=['initial_data.sql'])
async def test_search_remove(service_client):
    response = await service_client.post(
        '/v1/employee/add',
        headers={'Authorization': 'Bearer first_token'},
        json={'name': 'Fifth', 'surname': 'E', 'role': 'user'},
    )

    assert response.status == 200
    new_id = json.loads(response.text)['login']
    new_password = json.loads(response.text)['password']

    response = await service_client.post(
        '/v1/employee/remove',
        params={'employee_id': new_id},
        headers={'Authorization': 'Bearer first_token'},
        json={'name': 'Fifth', 'surname': 'E', 'role': 'user'},
    )

    assert response.status == 200

    response = await service_client.get(
        '/v1/search/intersect',
        json={'search_keys': ['Fifth'], 'limit': 1},
        headers={'Authorization': 'Bearer first_token'},
    )

    assert response.status == 200
    assert response.text == ('{"employees":[]}')

    response = await service_client.get(
        '/v1/search/intersect',
        json={'search_keys': ['E'], 'limit': 1},
        headers={'Authorization': 'Bearer first_token'},
    )

    assert response.status == 200
    assert response.text == ('{"employees":[]}')


@pytest.mark.pgsql('db_1', files=['initial_data.sql'])
async def test_search_edit(service_client):
    # Add phone
    response = await service_client.post(
        '/v1/profile/edit',
        headers={'Authorization': 'Bearer second_token'},
        json={'phones': ['+1111']},
    )

    assert response.status == 200

    response = await service_client.get(
        '/v1/search/intersect',
        json={'search_keys': ['+1111'], 'limit': 1},
        headers={'Authorization': 'Bearer second_token'},
    )

    assert response.status == 200
    assert response.text == ('{"employees":[{"id":"second_id"'
                             ',"name":"Second","surname":"B"}]}')

    # Add email
    response = await service_client.post(
        '/v1/profile/edit',
        headers={'Authorization': 'Bearer second_token'},
        json={'email': '2@mail.com'},
    )

    assert response.status == 200

    response = await service_client.get(
        '/v1/search/intersect',
        json={'search_keys': ['2@mail.com'], 'limit': 1},
        headers={'Authorization': 'Bearer second_token'},
    )

    assert response.status == 200
    assert response.text == ('{"employees":[{"id":"second_id"'
                             ',"name":"Second","surname":"B"}]}')

    # Edit phone
    response = await service_client.post(
        '/v1/profile/edit',
        headers={'Authorization': 'Bearer second_token'},
        json={'phones': ['+2222']},
    )

    assert response.status == 200
    response = await service_client.get(
        '/v1/search/intersect',
        json={'search_keys': ['+1111'], 'limit': 1},
        headers={'Authorization': 'Bearer second_token'},
    )

    assert response.status == 200
    assert response.text == ('{"employees":[]}')

    response = await service_client.get(
        '/v1/search/intersect',
        json={'search_keys': ['+2222'], 'limit': 1},
        headers={'Authorization': 'Bearer second_token'},
    )

    assert response.status == 200
    assert response.text == ('{"employees":[{"id":"second_id"'
                             ',"name":"Second","surname":"B"}]}')

    response = await service_client.get(
        '/v1/search/intersect',
        json={'search_keys': ['2@mail.com'], 'limit': 1},
        headers={'Authorization': 'Bearer second_token'},
    )

    assert response.status == 200
    assert response.text == ('{"employees":[{"id":"second_id"'
                             ',"name":"Second","surname":"B"}]}')


@pytest.mark.pgsql('db_1', files=['initial_data.sql'])
async def test_search_intersect(service_client):
    # basic intersect
    response = await service_client.post(
        '/v1/employee/add',
        headers={'Authorization': 'Bearer first_token'},
        json={'name': 'Seventh', 'surname': 'F', 'role': 'user'},
    )

    assert response.status == 200
    new_id = json.loads(response.text)['login']
    new_password = json.loads(response.text)['password']

    response = await service_client.get(
        '/v1/search/intersect',
        json={'search_keys': ['Seventh', 'F', 'user'], 'limit': 1},
        headers={'Authorization': 'Bearer first_token'},
    )

    assert response.status == 200
    response_required = Template('{"employees":[{"id":"${id}",'
                                 '"name":"Seventh","surname":"F"}]}')
    assert response.text == (response_required.substitute(id=new_id))

    # two people
    response = await service_client.post(
        '/v1/employee/add',
        headers={'Authorization': 'Bearer first_token'},
        json={'name': 'Eight', 'surname': 'F', 'role': 'user'},
    )

    assert response.status == 200
    new_id2 = json.loads(response.text)['login']
    new_password2 = json.loads(response.text)['password']

    response = await service_client.get(
        '/v1/search/intersect',
        json={'search_keys': ['Seventh', 'F'], 'limit': 5},
        headers={'Authorization': 'Bearer first_token'},
    )

    assert response.status == 200
    response_required = Template('{"employees":[{"id":"${id}",'
                                 '"name":"Seventh","surname":"F"},'
                                 '{"id":"${id2}",'
                                 '"name":"Eight","surname":"F"}]}')
    assert response.text == (response_required.substitute(id=new_id,
                                                          id2=new_id2))
    
    response = await service_client.get(
        '/v1/search/intersect',
        json={'search_keys': ['F'], 'limit': 10},
        headers={'Authorization': 'Bearer first_token'},
    )

    assert response.status == 200
    response_required = Template('{"employees":[{"id":"${id}",'
                                 '"name":"Seventh","surname":"F"},'
                                 '{"id":"${id2}",'
                                 '"name":"Eight","surname":"F"}]}')
    assert response.text == (response_required.substitute(id=new_id,
                                                          id2=new_id2))
    
    # three 
    response = await service_client.post(
        '/v1/employee/add',
        headers={'Authorization': 'Bearer first_token'},
        json={'name': 'Seventh', 'surname': 'G', 'role': 'user'},
    )

    assert response.status == 200
    new_id3 = json.loads(response.text)['login']
    new_password3 = json.loads(response.text)['password']

    response = await service_client.get(
        '/v1/search/intersect',
        json={'search_keys': ['Seventh', 'F'], 'limit': 10},
        headers={'Authorization': 'Bearer first_token'},
    )

    assert response.status == 200
    response_required = Template('{"employees":[{"id":"${id}",'
                                 '"name":"Seventh","surname":"F"},'
                                 '{"id":"${id2}",'
                                 '"name":"Eight","surname":"F"},'
                                 '{"id":"${id3}",'
                                 '"name":"Seventh","surname":"G"}]}')
    assert response.text == (response_required.substitute(id=new_id,
                                                          id2=new_id2,
                                                          id3=new_id3))


@pytest.mark.pgsql('db_1', files=['initial_data.sql'])
async def test_end(service_client):
    response = await service_client.post(
        '/v1/clear-tasks',
    )

    assert response.status == 200
