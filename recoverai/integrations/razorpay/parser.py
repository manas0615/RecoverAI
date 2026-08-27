from recoverai.domain.event import RevenueEvent


class RazorpayEventParser:
    @staticmethod
    def extract_reference_id(event: RevenueEvent) -> str | None:
        payload = event.metadata.get("payload", {})
        if not payload:
            return None
        payment_link = payload.get("payment_link", {})
        if not payment_link:
            return None
        entity = payment_link.get("entity", {})
        if not entity:
            return None
        return entity.get("reference_id")
