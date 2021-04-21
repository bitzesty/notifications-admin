from app import feedback_api_client


def test_create_broadcast_message(mocker):
    mock_post = mocker.patch(
        'app.notify_client.feedback_api_client.FeedbackAPIClient.post'
    )
    feedback_api_client.create_feedback(
        email='test@gov.uk',
        name='Name',
        message='msg'
    )
    mock_post.assert_called_once_with(
        url='/feedbacks',
        data={
            'email': 'test@gov.uk',
            'name': 'Name',
            'message': 'msg'
        }
    )
