from dynata_rex import OpportunityRegistry

registry = OpportunityRegistry('rex_access_key', 'rex_secret_key')

opportunities = registry.receive_notifications()

# Returns a list of Opportunity notifications
# [Opportunity(id=1,...), Opportunity(id=2,...), Opportunity(id=1,...)]
