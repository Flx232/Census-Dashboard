drop schema if exists pop_census cascade;
create schema pop_census;
set search_path to pop_census;

create table country (
    country_id serial primary key,
    alpha2 varchar(2) not null,
    alpha3 varchar(3) not null,
    area int,
    country_name varchar(350) not null
);

create table country_yr (
	country_yr_id serial primary key,
    country_id int not null
        references country(country_id),
    yr int not null
);

create table fertility_data(
	country_yr_id int not null
        references country_yr(country_yr_id),
    tfr decimal(25, 5),
    imr decimal(25, 5),
    e0 decimal(25, 5),
    births int,
    primary key(country_yr_id)
);

create table general_data(
	country_yr_id int not null
        references country_yr(country_yr_id),
    nim int,
    sexratio decimal(25, 5),
    natincr int,
    deaths int,
    gr int,
    primary key(country_yr_id)
);

create table gdp_data(
	country_yr_id int not null
        references country_yr(country_yr_id),
    gdp decimal(25, 5),
    primary key(country_yr_id)
);

create table pop_data(
	country_yr_id int not null
        references country_yr(country_yr_id),
    pop int,
    pop_dens decimal(25, 5),
    primary key(country_yr_id)
);

create table age_data(
	country_yr_id int not null
        references country_yr(country_yr_id),
    pop_young int,
    pop_middle int,
    pop_old int,
    births_young int,
    births_middle int,
    primary key(country_yr_id)
);