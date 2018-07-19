CREATE TABLE player (
	id INTEGER NOT NULL, 
	name VARCHAR, 
	pos VARCHAR, 
	yr INTEGER, 
	week INTEGER, 
	std_low FLOAT, 
	std_med FLOAT, 
	std_high FLOAT, 
	hppr_low FLOAT, 
	hppr_med FLOAT, 
	hppr_high FLOAT, 
	ppr_low FLOAT, 
	ppr_med FLOAT, 
	ppr_high FLOAT, 
	created_at DATETIME, 
	PRIMARY KEY (id),
    UNIQUE (name, yr, week)
)
