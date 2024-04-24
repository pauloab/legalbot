db.createUser({
	user: "legalbot",
	pwd: "L3gAl!12#",
	roles: [
		{
			role: "readWrite",
			db: "legalbot",
		},
		{
			role: "readWrite",
			db: "celery_tasks",
		},
	],
});
db = db.getSiblingDB("legalbot");
db.createCollection("chats");
db.createCollection("documents");

db = db.getSiblingDB("celery_tasks");
db.createCollection("default");
db.createCollection("taskmeta");
