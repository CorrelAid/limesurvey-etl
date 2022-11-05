# COPY THIS CODE TO YOUR SCRIPTS 
library(DBI)
library(readr)

# extract environment variables
ssh_ip <- Sys.getenv("LIMESURVEY_SSH_IP")
ssh_user <- Sys.getenv("LIMESURVEY_SSH_USER")
ssh_pw <- Sys.getenv("LIMESURVEY_SSH_PASSWORD")
sql_user <- Sys.getenv("LIMESURVEY_SQL_USER")
sql_password <- Sys.getenv("LIMESURVEY_SQL_PASSWORD")

# PREREQUISITE: ssh tunnel/port forwarding -> see README
con <- DBI::dbConnect(
  RMariaDB::MariaDB(), 
  dbname = "ve_limesurvey_test",
  host = "127.0.0.1", 
  port = 5555, 
  user = sql_user,
  password = sql_password)
# if you get error "Error: Failed to connect: Can't connect to MySQL server on '127.0.0.1' (36)" 
# make sure that you have a working SSH tunnel/port forwarding (see README)

# example command
DBI::dbListTables(con)

# disconnect
DBI::dbDisconnect(con)
