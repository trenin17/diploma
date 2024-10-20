INSERT INTO working_day_first.employees(id, name, surname)
VALUES ('first_id', 'First', 'A'),
       ('second_id', 'Second', 'B'),
       ('stranger_id', 'Stranger', 'S')
ON CONFLICT (id)
DO NOTHING;


INSERT INTO wd_general.auth_tokens(token, user_id, company_id, scopes)
VALUES ('zero_token', 'first_id', 'zero', ARRAY ['user', 'superuser']),
       ('first_token', 'first_id', 'first', ARRAY ['user', 'admin']),
       ('second_token', 'second_id', 'first', ARRAY ['user'])
ON CONFLICT (token)
DO NOTHING;

-- INSERT INTO working_day_first.documents(id, name, sign_required, description)
-- VALUES ('first_document', 'First', TRUE, 'First document'),
--        ('second_document', 'Second', FALSE, 'Second document')
    
-- INSERT INTO working_day_first.employee_document(employee_id, document_id, signed)
-- VALUES ('first_id', 'first_document', TRUE),
--        ('second_id', 'second_document', FALSE)

INSERT INTO working_day_first.teams(id, name) VALUES ('default_team', 'Default team'), ('stranger_team', 'Stranger team');
INSERT INTO working_day_first.employee_team(employee_id, team_id) VALUES ('first_id', 'default_team'), ('second_id', 'default_team'), ('stranger_id', 'stranger_team');