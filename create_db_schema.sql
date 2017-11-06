create table nodes (             
	id INTEGER PRIMARY KEY NOT NULL, 
	lat REAL,                        
	lon REAL,                        
	user TEXT,                       
	uid INTEGER,                     
	version INTEGER,                 
	changeset INTEGER,               
	timestamp TEXT                   
); 

create table nodes_tags(              
	id INTEGER,                          
	key TEXT,                            
	value TEXT,                          
	type TEXT,                           
	FOREIGN KEY(id) references nodes(id) 
);

create table ways (
	id INTEGER PRIMARY KEY NOT NULL,
	user TEXT,
	uid INTEGER,
	version TEXT,
	changeset INTEGER,
	timestamp TEXT
);  

create table ways_nodes (
	id INTEGER NOT NULL,
	node_id INTEGER NOT NULL,
	position INTEGER NOT NULL,
	FOREIGN KEY(id) references ways(id),
	FOREIGN KEY(node_id) references nodes(id)
);      

create table ways_tags (
	id INTEGER NOT NULL,
	key TEXT NOT NULL,
	value TEXT NOT NULL,
	type TEXT,
	FOREIGN KEY(id) references ways(id)
);    

.mode csv
.import nodes.csv nodes
.import nodes_tags.csv nodes_tags
.import ways.csv ways
.import ways_nodes.csv ways_nodes
.import ways_tags.csv ways_tags
