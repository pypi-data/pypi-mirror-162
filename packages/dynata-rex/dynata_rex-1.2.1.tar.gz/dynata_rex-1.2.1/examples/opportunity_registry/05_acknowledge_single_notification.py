from dynata_rex import OpportunityRegistry

registry = OpportunityRegistry('rex_access_key', 'rex_secret_key')

opportunities = registry.receive_notifications()

opportunity = opportunities[0]

registry.ack_notification(opportunity.id)
