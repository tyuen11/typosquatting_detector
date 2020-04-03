create schema dtd;
 
use dtd;

create table submittedUrls (original_url VARCHAR(255) PRIMARY KEY, date_added DATETIME NOT NULL, processing_start DATETIME, processing_finish DATETIME);
create table generatedUrls (generated_url VARCHAR(255) PRIMARY KEY, original_url VARCHAR(255), date_generated DATETIME NOT NULL, processing_start DATETIME, processing_finish DATETIME, generated_image MEDIUMTEXT, http_response_code TEXT);

ALTER DATABASE dtd CHARSET utf8mb4 COLLATE = utf8mb4_unicode_ci;
