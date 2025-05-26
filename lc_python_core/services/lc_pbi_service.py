def get_pbi_details(pbi_id: str) -> dict:
    print(f"[Stub] get_pbi_details called for: {pbi_id}")
    return {"status": "stubbed", "pbi_id": pbi_id}

def link_pbis(source_pbi: str, target_pbi: str) -> dict:
    print(f"[Stub] link_pbis called: {source_pbi} -> {target_pbi}")
    return {"status": "stubbed", "link": [source_pbi, target_pbi]}

def add_comment_to_pbi(pbi_id: str, comment: str) -> dict:
    print(f"[Stub] add_comment_to_pbi called for: {pbi_id}")
    return {"status": "stubbed", "commented": True, "pbi_id": pbi_id}
