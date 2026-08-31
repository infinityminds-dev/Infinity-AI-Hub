from datetime import datetime
import glob
import json


def smart_merge_memories():
    print("================================================================")
    print("   SMART AI MEMORY MERGE ENGINE V3.6 (Emoji & Master Safe)")
    print("================================================================\n")

    my_file = input(
        "Apni main file ka exact naam daalo (e.g. ai_memory_pankaj_master.json): "
    ).strip()

    if not my_file:
        print("Error: File ka naam dena zaroori hai!")
        return

    # 1. Master File Load Karo
    try:
        with open(my_file, "r", encoding="utf-8") as f:
            master_data = json.load(f)
            if not isinstance(master_data, list):
                master_data = []
    except Exception as e:
        print(f"Error: '{my_file}' kholne me problem aayi. Details: {e}")
        return

    tag_map = {}
    pattern_to_tag = {}

    for item in master_data:
        if not isinstance(item, dict):
            continue
        tag = item.get("tag", "general")
        patterns = set(
            str(p).strip() for p in item.get("patterns", []) if str(p).strip()
        )
        responses = list(item.get("responses", []))
        ctx_resp = item.get("context_responses", {})

        if tag not in tag_map:
            tag_map[tag] = {
                "patterns": patterns,
                "responses": responses,
                "context_responses": ctx_resp,
            }
        else:
            tag_map[tag]["patterns"].update(patterns)
            for r in responses:
                if r not in tag_map[tag]["responses"]:
                    tag_map[tag]["responses"].append(r)
            tag_map[tag]["context_responses"].update(ctx_resp)

        for p in patterns:
            pattern_to_tag[p.lower()] = tag

    # 2. Dosto ki files search karo
    all_files = glob.glob("ai_memory_*.json")
    friend_files = [f for f in all_files if f != my_file]

    if not friend_files:
        print("Folder me merge karne ke liye kisi dost ki memory file nahi mili!")
        return

    print(f"Mili hui dosto ki files: {friend_files}\n")
    added_patterns_count = 0

    # 3. Smart Merging with Emoji & UTF-8 Compatibility
    for file_path in friend_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                friend_data = json.load(f)
                if not isinstance(friend_data, list):
                    continue

                for item in friend_data:
                    if not isinstance(item, dict):
                        continue
                    f_tag = item.get("tag", "general")
                    f_patterns = [
                        str(p).strip()
                        for p in item.get("patterns", [])
                        if str(p).strip()
                    ]
                    f_responses = item.get("responses", [])
                    f_ctx = item.get("context_responses", {})

                    if f_tag not in tag_map:
                        tag_map[f_tag] = {
                            "patterns": set(),
                            "responses": [],
                            "context_responses": {},
                        }

                    for p in f_patterns:
                        # Fix: Check global pattern map to prevent duplicate learning
                        if p.lower() not in pattern_to_tag:
                            tag_map[f_tag]["patterns"].add(p)
                            pattern_to_tag[p.lower()] = f_tag
                            added_patterns_count += 1

                    for r in f_responses:
                        if r not in tag_map[f_tag]["responses"]:
                            tag_map[f_tag]["responses"].append(r)

                    tag_map[f_tag]["context_responses"].update(f_ctx)

        except Exception as e:
            print(f"File {file_path} read karne me error: {e}")

    # 4. Rebuild Final Clean Master JSON Structure
    final_master_list = []
    for tag, details in tag_map.items():
        if details["patterns"] and details["responses"]:
            final_master_list.append(
                {
                    "tag": tag,
                    "patterns": list(details["patterns"]),
                    "responses": details["responses"],
                    "context_responses": details["context_responses"],
                }
            )

    # 5. Save Back to Master File
    with open(my_file, "w", encoding="utf-8") as f:
        json.dump(final_master_list, f, indent=2, ensure_ascii=False)

    print(
        f"\nSUCCESS! Total {added_patterns_count} naye patterns dosto ki files se '{my_file}' me safely merge ho gaye!"
    )
    print("V3.6 & V4.0 Neural Engine structure fully intact. 😎🔥")


if __name__ == "__main__":
    smart_merge_memories()
