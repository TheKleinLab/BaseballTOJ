CREATE TABLE participants (
	id integer primary key autoincrement not null,
	userhash text not null,
	random_seed text not null,
	sex text not null,
	age integer not null, 
	handedness text not null,
  created text not null
);

CREATE TABLE surveys (
  id integer primary key autoincrement not null,
  participant_id integer key not null,
  tie_run_familiar text not null,
  tie_run_used text not null
);

CREATE TABLE trials (
	id integer primary key autoincrement not null,
	participant_id integer key not null,
	block_num integer not null,
	trial_num integer not null,
	soa integer not null,
  baserun_offset integer not null,
	first_arrival text not null,
	probed_trial text not null,
  glove_probe_dist text not null,
  base_probe_dist text not null,
	probe_location text not null,
	probe_color text not null,
  color_response text not null,
  color_diff text not null,
  toj_response text not null,
	response_time text not null
);
