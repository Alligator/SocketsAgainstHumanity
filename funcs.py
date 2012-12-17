def IsNameTaken(name):
  global clients
  
  for key in clients.iterkeys():
    if clients[key].nickname == name:
      return True
  return False  
