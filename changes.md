In Supabase, there is a table called "subpages" that contains URLs in the full_url column. Each URL should be scraped.

For each URL scraped:

The extracted data should be stored in a table called "scraped_data2".

The corresponding row in "scraped_data2" should include:

subpage_id: the id from the subpages table associated with the URL.

json: a JSON object containing the extracted fields (see below).

scraped_at: the timestamp when the data was scraped.

The fields to extract from each URL are:

company location

company overview

investment criteria

investment strategy

portfolio companies

team/leadership: each entry should include name, associated bio, and role

Please write the logic to:

Loop through all rows in the subpages table

Extract the fields listed above

Insert one record into scraped_data2 per URL