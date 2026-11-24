from db.mongo import get_db
 
print(get_db().command("ping"))