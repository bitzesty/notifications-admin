import pytest
from flask import session, url_for

from app.utils import is_gov_user
from tests import organisation_json
from tests.conftest import normalize_spaces


def test_non_gov_user_cannot_see_add_service_button(
    client,
    mock_login,
    mock_get_non_govuser,
    api_nongov_user_active,
    mock_get_organisations,
    mock_get_organisations_and_services_for_user,
):
    client.login(api_nongov_user_active)
    response = client.get(url_for('main.choose_account'))
    assert 'Add a new service' not in response.get_data(as_text=True)
    assert response.status_code == 200


@pytest.mark.parametrize('org_json', (
    None,
    organisation_json(organisation_type=None),
))
def test_get_should_render_add_service_template(
    client_request,
    mocker,
    org_json,
):
    mocker.patch(
        'app.organisations_client.get_organisation_by_domain',
        return_value=org_json,
    )
    page = client_request.get('main.add_service')
    assert page.select_one('h1').text.strip() == 'About your service'
    assert page.select_one('input[name=name]').get('value') is None
    assert [
        label.text.strip() for label in page.select('.govuk-radios__item label')
    ] == [
        'Charity',
        'Community Interest Company',
        'Other',
    ]
    assert [
        radio['value'] for radio in page.select('.govuk-radios__item input')
    ] == [
        'charity',
        'community_interest',
        'other',
    ]


def test_get_should_not_render_radios_if_org_type_known(
    client_request,
    mocker,
):
    mocker.patch(
        'app.organisations_client.get_organisation_by_domain',
        return_value=organisation_json(organisation_type='central'),
    )
    page = client_request.get('main.add_service')
    assert page.select_one('h1').text.strip() == 'About your service'
    assert page.select_one('input[name=name]').get('value') is None
    assert not page.select('.multiple-choice')


def test_show_different_page_if_user_org_type_is_local(
    client_request,
    mocker,
):
    mocker.patch(
        'app.organisations_client.get_organisation_by_domain',
        return_value=organisation_json(organisation_type='local'),
    )
    page = client_request.get('main.add_service')
    assert page.select_one('h1').text.strip() == 'About your service'
    assert page.select_one('input[name=name]').get('value') is None
    assert page.select_one('main .govuk-body').text.strip() == (
        'Give your service a name that tells users what your '
        'messages are about, as well as who they’re from. For example:')


@pytest.mark.parametrize('email_address', (
    # User’s email address doesn't matter when the organisation is known
    'test@example.gov.uk',
    'test@example.nhs.uk',
))
@pytest.mark.parametrize('inherited, posted, persisted, sms_limit', (
    (None, 'charity', 'charity', 1000),
    ('charity', None, 'charity', 1000),
    (None, 'community_interest', 'community_interest', 1000),
    ('community_interest', None, 'community_interest', 1000),
    (None, 'other', 'other', 1000),
    ('other', None, 'other', 1000)
))
def test_should_add_service_and_redirect_to_tour_when_no_services(
    mocker,
    client_request,
    mock_create_service,
    mock_create_service_template,
    mock_get_services_with_no_services,
    api_user_active,
    mock_create_or_update_free_sms_fragment_limit,
    mock_get_all_email_branding,
    inherited,
    email_address,
    posted,
    persisted,
    sms_limit,
):
    api_user_active['email_address'] = email_address
    client_request.login(api_user_active)
    mocker.patch(
        'app.organisations_client.get_organisation_by_domain',
        return_value=organisation_json(organisation_type=inherited),
    )
    client_request.post(
        'main.add_service',
        _data={
            'name': 'testing the post',
            'service_description': 'description',
            'organisation_type': posted,
        },
        _expected_status=302,
        _expected_redirect=url_for(
            'main.begin_tour',
            service_id=101,
            template_id="Example%20text%20message%20template",
            _external=True,
        ),
    )
    assert mock_get_services_with_no_services.called
    mock_create_service.assert_called_once_with(
        service_name='testing the post',
        service_description='description',
        organisation_type=persisted,
        message_limit=50,
        restricted=True,
        user_id=api_user_active['id'],
        email_from='testing.the.post',
    )
    mock_create_service_template.assert_called_once_with(
        'Example text message template',
        'sms',
        (
            'Hey ((name)), I’m trying out Notify. Today is '
            '((day of week)) and my favourite colour is ((colour)).'
        ),
        101,
    )
    assert session['service_id'] == 101
    mock_create_or_update_free_sms_fragment_limit.assert_called_once_with(101, sms_limit)


def test_add_service_has_to_choose_org_type(
    mocker,
    client_request,
    mock_create_service,
    mock_create_service_template,
    mock_get_services_with_no_services,
    api_user_active,
    mock_create_or_update_free_sms_fragment_limit,
    mock_get_all_email_branding,
):
    mocker.patch(
        'app.organisations_client.get_organisation_by_domain',
        return_value=None,
    )
    page = client_request.post(
        'main.add_service',
        _data={
            'name': 'testing the post',
        },
        _expected_status=200,
    )
    assert normalize_spaces(page.select_one('.govuk-error-message').text) == (
        'Error: Select the type of organisation'
    )
    assert mock_create_service.called is False
    assert mock_create_service_template.called is False
    assert mock_create_or_update_free_sms_fragment_limit.called is False


@pytest.mark.parametrize('email_address', (
    'test@nhs.net',
    'test@nhs.uk',
    'test@example.NhS.uK',
    'test@EXAMPLE.NHS.NET',
))
def test_get_should_only_show_nhs_org_types_radios_if_user_has_nhs_email(
    client_request,
    mocker,
    api_user_active,
    email_address,
):
    api_user_active['email_address'] = email_address
    client_request.login(api_user_active)
    mocker.patch(
        'app.organisations_client.get_organisation_by_domain',
        return_value=None,
    )
    page = client_request.get('main.add_service')
    assert page.select_one('h1').text.strip() == 'About your service'
    assert page.select_one('input[name=name]').get('value') is None
    assert page.select_one('input[name=service_description]').get('value') is None
    assert [
        label.text.strip() for label in page.select('.govuk-radios__item label')
    ] == []
    assert [
        radio['value'] for radio in page.select('.govuk-radios__item input')
    ] == []


@pytest.mark.parametrize('organisation_type, free_allowance', [
    ('charity', 1000),
    ('community_interest', 1000),
    ('other', 1000),
])
def test_should_add_service_and_redirect_to_dashboard_when_existing_service(
    app_,
    mocker,
    client_request,
    mock_create_service,
    mock_create_service_template,
    mock_get_services,
    mock_get_no_organisation_by_domain,
    api_user_active,
    organisation_type,
    free_allowance,
    mock_create_or_update_free_sms_fragment_limit,
    mock_get_all_email_branding,
):
    client_request.post(
        'main.add_service',
        _data={
            'name': 'testing the post',
            'service_description': 'description',
            'organisation_type': organisation_type,
        },
        _expected_status=302,
        _expected_redirect=url_for(
            'main.service_dashboard',
            service_id=101,
            _external=True,
        )
    )
    assert mock_get_services.called
    mock_create_service.assert_called_once_with(
        service_name='testing the post',
        service_description='description',
        organisation_type=organisation_type,
        message_limit=app_.config['DEFAULT_SERVICE_LIMIT'],
        restricted=True,
        user_id=api_user_active['id'],
        email_from='testing.the.post',
    )
    mock_create_or_update_free_sms_fragment_limit.assert_called_once_with(101, free_allowance)
    assert len(mock_create_service_template.call_args_list) == 0
    assert session['service_id'] == 101


@pytest.mark.parametrize('name, error_message', [
    ('', 'Cannot be empty'),
    ('.', 'Must include at least two alphanumeric characters'),
    ('a' * 256, 'Service name must be 255 characters or fewer'),
])
def test_add_service_fails_if_service_name_fails_validation(
    client_request,
    mock_get_organisation_by_domain,
    name,
    error_message,
):
    page = client_request.post(
        'main.add_service',
        _data={"name": name},
        _expected_status=200,
    )
    assert error_message in page.find("span", {"class": "govuk-error-message"}).text


def test_should_return_form_errors_with_duplicate_service_name_regardless_of_case(
    client_request,
    mock_create_duplicate_service,
    mock_get_organisation_by_domain,
):
    page = client_request.post(
        'main.add_service',
        _data={
            'name': 'SERVICE ONE',
            'service_description': 'description',
            'organisation_type': 'other',
        },
        _expected_status=200,
    )
    assert 'This service name is already in use' in page.select_one('.govuk-error-message').text.strip()


def test_non_government_user_can_access_create_service_page(
    client_request,
    mock_get_non_govuser,
    api_nongov_user_active,
    mock_get_organisations,
    mock_get_organisation_by_domain,
):
    assert is_gov_user(api_nongov_user_active['email_address']) is False
    client_request.get(
        'main.add_service',
        _expected_status=200,
    )


def test_non_government_user_can_create_service(
    client_request,
    mock_get_non_govuser,
    api_nongov_user_active,
    mock_get_organisations,
    mock_get_organisation_by_domain,
):
    assert is_gov_user(api_nongov_user_active['email_address']) is False
    client_request.post(
        'main.add_service',
        _data={'name': 'SERVICE TWO'},
        _expected_status=200,
    )
