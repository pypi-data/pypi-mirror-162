from schema import Schema, Optional, And, Or, Use
from datetime import date

skills = [Or(
    str,
    {
        'name': str,
        Optional('level'): And(Or(int, float), lambda n: 0 <= n <= 10),
        Optional('level-worded'): str,
        Optional(str): object
    }
)]

schema = Schema({
    # Self description
    Optional('title'): str,
    Optional('fullname'): str,
    'firstname': str,
    'lastname': str,
    Optional('middlenames'): [str],
    Optional('pronouns'): str,
    'headline': str,
    # Introduction
    Optional('about'): str,
    # Info
    Optional('location'): str,
    'contact': {
        Or(
            'numbers',
            'emails'
        ): [str],
        Optional(str): object
    },
    Optional('links'): [{
        Optional('type', default='link'): And(
            str,
            Use(str.lower),
            lambda s: s in ('social', 'portfolio', 'website', 'link')
        ),
        Optional('description'): str,
        'link': str,
        Optional(str): object
    }],
    # Experience
    Optional('experience'): [{
        'title': str,
        'type': str,
        'org': str,
        'location': str,
        'start_date': date,
        Optional('end_date', default=None): Or(None, date),
        Optional('description'): str,
        Optional('skills'): skills,
        Optional(str): object
    }],
    # Education
    Optional('education'): [{
        'school': str,
        Or(
            'degree',
            'degree_shortname'
        ): str,
        'field_of_study': str,
        'start_date': date,
        Optional('end_date', default=None): Or(None, date),
        Optional('result'): str,
        Optional('activities'): str,
        Optional('description'): str,
        Optional(str): object
    }],
    # Certifications/Licences
    Optional('certifications'): [{
        'name': str,
        'issuer': str,
        'issue_date': date,
        Optional('expiry_date', default=None): Or(None, date),
        Optional('credential_id'): str,
        Optional('credential_url'): str,
        Optional(str): object
    }],
    # Skills
    Optional('skills'): Or(
        {str: skills},
        skills
    ),
    # References
    Optional('references'): [{
        'name': str,
        'title': str,
        'contact': {
            Or(
                'numbers',
                'emails'
            ): [str],
            Optional(str): object
        },
        Optional('note'): str,
        Optional(str): object
    }],
    # Interests/Hobbies
    Optional('interests'): [{
        'title': str,
        'description': str,
        Optional(str): object
    }],
    # Allow additional values
    Optional(str): object
})
