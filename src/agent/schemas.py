from pydantic import BaseModel, Field


class ProspectInfoSchema(BaseModel):
    """Schema for prospect information."""
    name: str = Field(description="The name of the sales prospect")
    email: str = Field(description="The email of the sales prospect")
    company: str = Field(description="The company of the sales prospect")
    website: str | None = Field(
        default=None,
        description="The website of the sales prospect")
    door_count: str = Field(description="The door count of the sales prospect")
    property_management_software: str = Field(
        description="The property management software of the sales prospect"
    )
    notes: str | None = Field(
        default=None,
        description="Any additional notes about the sales prospect"
    )


class EmailContentSchema(BaseModel):
    """Schema for email content."""
    subject: str = Field(description="The subject of the AI generated email")
    body: str = Field(description="The body of the AI generated email")


class FeedbackSchema(BaseModel):
    """Schema for feedback."""
    feedback: str = Field(description="User feedback about the AI generated email")

class UserPreferences(BaseModel):
    """Updated user preferences based on user's feedback."""
    chain_of_thought: str = Field(description="Reasoning about which user preferences need to add/update if required")
    user_preferences: str = Field(description="Updated user preferences")