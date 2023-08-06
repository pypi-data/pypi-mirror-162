from redflagbpm.BPMService import BPMService
from redflagbpm.Services import Service, DocumentService, Context, ResourceService


def setupServices(self: BPMService):
    self.service = Service(self)
    self.documentService = DocumentService(self)
    self.context = Context(self)
    self.resourceService = ResourceService(self)

BPMService.setupServices = setupServices
