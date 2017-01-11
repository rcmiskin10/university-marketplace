# university-marketplace

A university marketplace where students within a school log in to the marketplace platform and can buy and sell products/services between eachother. If you do not have the specific schools email address it will not allow you in.

The first two test schools are Brandeis University and UMass-Amherst.

This repo only consists of local settings and does not include settings for production, or AWS settings for S3.

It can be seen at studentgrounds.org, and you can test it out by logging into test123@test.com using password: test123.

It is written using Python/Django, sqlite3 for the database in local environment, and postgresql for production on Heroku. Front end written with HTML, CSS, JQuery and Javascript along with bootstrap for responsiveness. Dependencies are in requirements.txt file.