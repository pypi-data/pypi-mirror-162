def merge_ranges(ranges):
  ordered = sorted(ranges, key=lambda x: x[0])
  purified = []
  index = 0
  while index < len(ordered)-1:
    first, second = ordered[index], ordered[index+1]
    if first[1] > second[0]:
      purified.append((first[0], max(first[1], second[1]), first[2]))
      index = index + 2
    else:
      purified.append(first)
      index = index + 1
  if index == len(ordered)-1:
    purified.append(ordered[index])
  return purified

def extend_ranges(ranges, maxlen):
  ordered = merge_ranges(ranges)
  start = 0
  result = []
  for e in ordered:
    if start < e[0]:
      result.append((start, e[0], "plain"))
    result.append(e)
    start = e[1]
  if start < maxlen:
    result.append((start, maxlen, "plain"))
  return result

def explain(kg, translator):
  d = {}
  for k, v in kg.items():
    if k in translator.keys():
      d[translator[k]] = v
    else:
      d[k] = v
  return d
