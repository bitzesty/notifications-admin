from app.notify_client import NotifyAdminAPIClient


class FeedbackAPIClient(NotifyAdminAPIClient):

    def create_feedback(self, email, name, message):
        return self.post(
            url="/feedbacks",
            data={
                "email": email,
                "name": name,
                "message": message
            }
        )


feedback_api_client = FeedbackAPIClient()
