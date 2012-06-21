def enum(*seq):
  enum_dict = dict(zip(seq, range(len(seq))))
  return type('enum', (), enum_dict)
