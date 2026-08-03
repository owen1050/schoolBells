import sqlite3, uuid, traceback, json, bcrypt

class databaseQuerys:

	con = -1
	cur = -1
	encoder = json.JSONEncoder()

	def __init__(self, db = "prod.db"):
		self.con = sqlite3.connect(db, check_same_thread=False)

	def dbCheck(self):
		#returns "{"status" : '#'}"
			#status -1 is error
			#status 0 is okay
		try:
			ret = self.executeSQL("SELECT * FROM leagues")
			return {"status" : '0'}
		except Exception as e:
			print("error in dbCheck", e)
			return {"status" : '-1'}

	def executeSQL(self, sqlCommand, forceNoCommit = False):
		self.cur = self.con.cursor()
		res = self.cur.execute(sqlCommand)
		ret = res.fetchall()

		if((sqlCommand.find("insert") != -1 or sqlCommand.find("delete") != -1 or sqlCommand.find("update") != -1) and forceNoCommit == False):
			self.con.commit()
		return ret

