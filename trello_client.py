import requests
import sys

auth_params = {    
  'key': "de929ad698e8c565a65d6e0c37c5c2e4",    
  'token': "096d4b4c6f1b0925b29a7ac3e5e90d0cd8558efba8d93f2c425f726694d4d20b", 
  }  
   
base_url = "https://api.trello.com/1/{}"
board_id = "5B6gGDGZ"  

def read():
  column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()       
  for column in column_data:      
    print(column['name'])         
    task_data = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()      
    if not task_data:      
      print('\t' + 'Нет задач!')      
      continue      
    for task in task_data:      
      print('\t' + task['name'])

def create(name, column_name):          
  column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()         
  for column in column_data:      
    if column['name'].split('(')[0].rstrip() == column_name:        
      requests.post(base_url.format('cards'), data={'name': name, 'idList': column['id'], **auth_params})      
      break

def move(name, column_name):     
  column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()      
  task_id = None    
  for column in column_data:    
    column_tasks = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()    
    for task in column_tasks:    
      if task['name'] == name:    
        task_id = task['id']    
        break    
      if task_id:    
        break    
  for column in column_data:    
    if column['name'].split('(')[0].rstrip() == column_name:        
      requests.put(base_url.format('cards') + '/' + task_id + '/idList', data={'value': column['id'], **auth_params})    
      break  

def getLongBoardId(board_id):
  board_data = requests.get(base_url.format('boards') + '/' + board_id, params=auth_params).json()
  return board_data['id']

def columnCreate(new_column_name):
  column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()
  for column in column_data:
    if (column['name'].split('(')[0].rstrip() == new_column_name):
      print('Лист с названием {} уже существует! Придумайте другое название..\n'.format(new_column_name))
      return False
  longBoardId = getLongBoardId(board_id)
  requests.post(base_url.format('lists'), data={'idBoard': longBoardId, 'name': new_column_name, **auth_params})
  print('Лист {} успешно создан!\n'.format(new_column_name))
  return True

def archiveList(column_name):
  column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()
  for column in column_data:
    if (column['name'].split('(')[0].rstrip() == column_name):
      requests.put(base_url.format('lists/') + column['id'] + '/closed', data={'value': 'true', **auth_params})
      print('Лист {} успешно отправлен в архив!'.format(column_name))
      return True
  print('Листа с названием {} не существует!'.format(column_name))
  return False

def updateColumnName():
  column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()
  for column in column_data:
    column_tasks = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
    newColumnName = '{} ({})'.format(column['name'].split('(')[0].rstrip(), len(column_tasks))
    requests.put(base_url.format('lists') + '/' + column['id'], data = {'name' : newColumnName, **auth_params})

def getAvailableLists():
  column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()
  listsDict = {}
  i = 0
  for column in column_data:
    i += 1
    listsDict[str(i)] = column['name'].split('(')[0].rstrip()
  return listsDict


if __name__ == "__main__":
  try:
    response = requests.get(base_url.format('boards') + '/' + board_id, params=auth_params)
    response.raise_for_status()
  except requests.exceptions.HTTPError as e:
    print('Не удалось получить данные от {}\n{}\nЗавершение программы..'.format(response.url,e))
    sys.exit()
  while(True):
    print('\nCLI для работы с доской {} на trello.com'.format(response.json()['name']))
    print('\nМеню:')
    print('\t 1 - Показать доску')
    print('\t 2 - Добавить лист')
    print('\t 3 - Архивировать лист')
    print('\t 4 - Добавить задачу')
    print('\t 5 - Переместить задачу')
    print('\t 6 - Выход\n')
    choose = input('Делайте Ваш выбор: -> ')
    if (choose == '1'):
      updateColumnName()
      read()
    elif (choose == '2'):
      result = False
      while(result is not True):
        new_column_name = input('Введите название нового листа: -> ')
        result = columnCreate(new_column_name)
    elif (choose == '3'):
      availableLists = {}
      flag = False
      availableLists = getAvailableLists()
      print('\nДоступные листы:')
      for availableList in availableLists:
        print('\t{} - {}'.format(availableList, availableLists[availableList]))
      while (flag is not True):
        column_name = input('Введите номер листа, который необходимо отправить в архив: -> ')
        try:
          archiveList(availableLists[column_name])
        except KeyError:
          print('\nНе корректный номер листа')
          continue
        flag = True
      
    elif (choose == '6'):
      print('Завершение программы..')
      sys.exit()


    