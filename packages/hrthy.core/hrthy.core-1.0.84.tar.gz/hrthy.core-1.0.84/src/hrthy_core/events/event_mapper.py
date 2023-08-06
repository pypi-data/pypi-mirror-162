from hrthy_core.events.events.candidate_event import (
    CandidateCreatedEvent, CandidateInvitedEvent, CandidateLoggedInEvent, CandidateLoggedOutEvent,
    CandidateLoginRefreshedEvent, CandidateUpdatedEvent,
)
from hrthy_core.events.events.company_event import (
    CompanyCreatedEvent, CompanyDeletedEvent, CompanyRestoredEvent, CompanyUpdatedEvent,
)
from hrthy_core.events.events.pipeline_event import (
    PipelineCandidateAssignedEvent, PipelineCandidateUnassignedEvent, PipelineCreatedEvent, PipelineDeletedEvent,
    PipelineUpdatedEvent,
)
from hrthy_core.events.events.role_event import RoleCreatedEvent, RoleDeletedEvent, RoleUpdatedEvent
from hrthy_core.events.events.user_event import (
    UserAcceptedInvitationEvent, UserCreatedEvent, UserDeletedEvent, UserInvitedEvent, UserLoggedInEvent,
    UserLoggedOutEvent, UserLoginRefreshedEvent, UserRestoredEvent, UserUpdatedEvent,
)

event_mapping = {
    # Company
    'CompanyCreatedEvent': CompanyCreatedEvent,
    'CompanyUpdatedEvent': CompanyUpdatedEvent,
    'CompanyDeletedEvent': CompanyDeletedEvent,
    'CompanyRestoredEvent': CompanyRestoredEvent,
    # User
    'UserCreatedEvent': UserCreatedEvent,
    'UserUpdatedEvent': UserUpdatedEvent,
    'UserDeletedEvent': UserDeletedEvent,
    'UserInvitedEvent': UserInvitedEvent,
    'UserRestoredEvent': UserRestoredEvent,
    'UserAcceptedInvitationEvent': UserAcceptedInvitationEvent,
    # Role
    'RoleCreatedEvent': RoleCreatedEvent,
    'RoleUpdatedEvent': RoleUpdatedEvent,
    'RoleDeletedEvent': RoleDeletedEvent,
    # User Auth
    'UserLoggedInEvent': UserLoggedInEvent,
    'UserLoggedOutEvent': UserLoggedOutEvent,
    'UserLoginRefreshedEvent': UserLoginRefreshedEvent,
    # Candidate
    'CandidateCreatedEvent': CandidateCreatedEvent,
    'CandidateUpdatedEvent': CandidateUpdatedEvent,
    'CandidateInvitedEvent': CandidateInvitedEvent,
    # Candidate Auth
    'CandidateLoggedInEvent': CandidateLoggedInEvent,
    'CandidateLoggedOutEvent': CandidateLoggedOutEvent,
    'CandidateLoginRefreshedEvent': CandidateLoginRefreshedEvent,
    # Pipeline
    'PipelineCreatedEvent': PipelineCreatedEvent,
    'PipelineUpdatedEvent': PipelineUpdatedEvent,
    'PipelineDeletedEvent': PipelineDeletedEvent,
    'PipelineCandidateAssignedEvent': PipelineCandidateAssignedEvent,
    'PipelineCandidateUnassignedEvent': PipelineCandidateUnassignedEvent
}
