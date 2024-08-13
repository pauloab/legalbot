db = db.getSiblingDB("legalbot");
if (!db.getCollectionNames().includes("chats")) {
	db.createCollection("chats", { collation: { locale: "en", strength: 2 } });
}
if (!db.getCollectionNames().includes("documents")) {
	db.createCollection("documents", {
		collation: { locale: "en", strength: 2 },
	});
}

db = db.getSiblingDB("celery_tasks");
if (!db.getCollectionNames().includes("default")) {
	db.createCollection("default", {
		collation: { locale: "en", strength: 2 },
	});
}
if (!db.getCollectionNames().includes("taskmeta")) {
	db.createCollection("taskmeta", {
		collation: { locale: "en", strength: 2 },
	});
}

if (!db.getUser("legalbot")) {
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
}
