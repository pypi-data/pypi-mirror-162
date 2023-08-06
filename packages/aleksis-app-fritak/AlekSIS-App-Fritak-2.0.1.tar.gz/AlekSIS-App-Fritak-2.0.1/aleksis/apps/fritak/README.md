# school-apps: Fritak (exemption requests)
### Workflow

1. Teacher fills out form

    - Start date (DateField)
    - Start hour or time (Int 1..9 / Time)
    - End Date (DateField)
    - End of hour or time (Int 1..9 / Time)
    - Description (TextField)
    - Applicant (teacher code) is automatically generated from registered user

2. Headmaster receives request (link by mail) and a. approves or b. rejects

    a. Alternate reviews request and i. approves or ii. raises concerns and rejects

        i. Deputy enters absence in the substitution plan. Teacher receives positive feedback.

        ii. Request goes back to the headmaster, who finally aa. approves or b. rejects.

    b. Teacher receives rejection with reasons

