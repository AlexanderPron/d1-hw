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
  # Получим данные всех колонок на доске      
  column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()      
    
  # Переберём данные обо всех колонках, пока не найдём ту колонку, которая нам нужна      
  for column in column_data:      
    if column['name'].split('(')[0].rstrip() == column_name:      
        # Создадим задачу с именем _name_ в найденной колонке      
      requests.post(base_url.format('cards'), data={'name': name, 'idList': column['id'], **auth_params})      
      break

def move(name, column_name):    
  # Получим данные всех колонок на доске    
  column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()    
      
  # Среди всех колонок нужно найти задачу по имени и получить её id    
  task_id = None    
  for column in column_data:    
    column_tasks = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()    
    for task in column_tasks:    
      if task['name'] == name:    
        task_id = task['id']    
        break    
      if task_id:    
        break    
  # Теперь, когда у нас есть id задачи, которую мы хотим переместить    
  # Переберём данные обо всех колонках, пока не найдём ту, в которую мы будем перемещать задачу    
  for column in column_data:    
    if column['name'].split('(')[0].rstrip() == column_name:    
      # И выполним запрос к API для перемещения задачи в нужную колонку    
      requests.put(base_url.format('cards') + '/' + task_id + '/idList', data={'value': column['id'], **auth_params})    
      break  
def columnCreate(new_column_name):
  longBoardId = getLongBoardId(board_id)
  res = requests.post(base_url.format('lists'), data={'idBoard': longBoardId, 'name': new_column_name, **auth_params})
  print(res.text)

def getLongBoardId(board_id):
  board_data = requests.get(base_url.format('boards') + '/' + board_id, params=auth_params).json()
  return board_data['id']

def updateColumnName():
  column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()
  for column in column_data:
    column_tasks = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
    newColumnName = '{} ({})'.format(column['name'].split('(')[0].rstrip(), len(column_tasks))
    requests.put(base_url.format('lists') + '/' + column['id'], data = {'name' : newColumnName, **auth_params})


if __name__ == "__main__":
  updateColumnName()
  if len(sys.argv) <= 2:    
    read()
  elif sys.argv[1] == 'create-column':    
    columnCreate(sys.argv[2])
    updateColumnName()    
  elif sys.argv[1] == 'create':    
    create(sys.argv[2], sys.argv[3])
    updateColumnName()    
  elif sys.argv[1] == 'move':    
    move(sys.argv[2], sys.argv[3])
    updateColumnName() 