#!/usr/bin/env python3
import os, json
import db

c = db.get_client()

r1 = c.from_('executive_summary').select('id,generated_at,data').eq('id','current').single().execute()
d = r1.data
data = d['data'] if isinstance(d['data'], dict) else json.loads(d['data'])
print('executive_summary:')
print('  table generated_at:', d['generated_at'])
print('  data  generated_at:', data.get('generated_at'))

r2 = c.from_('operational_briefing').select('id,generated_at,data').eq('id','current').single().execute()
d2 = r2.data
data2 = d2['data'] if isinstance(d2['data'], dict) else json.loads(d2['data'])
print()
print('operational_briefing:')
print('  table generated_at:', d2['generated_at'])
print('  data  generated_at:', data2.get('generated_at'))
