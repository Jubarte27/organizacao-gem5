import sys

import pandas as pd
import re

def parse_gem5_stats_to_dataframe(filepath):
  data = []
  
  stat_pattern = re.compile(r'^\s*([a-zA-Z0-9_\.:-]+)\s+([^#]+?)\s*#\s*(.*)$')
  
  with open(filepath, 'r', encoding='utf-8') as file:
    for line in file:
      line = re.sub(r'\\', '', line).strip()
      
      if not line or line.startswith('---'):
        continue
      
      match = stat_pattern.match(line)
      if match:
        metric = match.group(1).strip()
        raw_values : str = match.group(2).strip()
        description = match.group(3).strip()
        
        tokens = raw_values.split()
        primary_value_str = tokens[0] if tokens else ""
        
        try:
          primary_value = float(primary_value_str)
        except (ValueError, TypeError):
          primary_value = primary_value_str
        
        data.append({
          'Metric': metric,
          'Value': primary_value,
          'Description': description,
          'Raw_Values': raw_values
        })
              
  df = pd.DataFrame(data)
  return df

if __name__ == '__main__':
  parse_gem5_stats_to_dataframe(sys.argv[1])