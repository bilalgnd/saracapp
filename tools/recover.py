import json

latest_code = ""
with open(r'C:\Users\bilal\.gemini\antigravity\brain\5cc59c14-abc6-41bf-bb85-4bd163906ff8\.system_generated\logs\transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        try:
            data = json.loads(line)
            if 'tool_calls' in data:
                for tc in data['tool_calls']:
                    if tc.get('name') == 'default_api:write_to_file':
                        args = tc.get('arguments', {})
                        if 'ui.py' in args.get('TargetFile', ''):
                            latest_code = args.get('CodeContent', '')
        except Exception:
            pass

if latest_code:
    with open(r'C:\Users\bilal\SARACAPP\ui_recovered.py', 'w', encoding='utf-8') as out:
        out.write(latest_code)
    print(f"Recovered successfully! Size: {len(latest_code)}")
else:
    print("Could not find ui.py in tool calls.")
