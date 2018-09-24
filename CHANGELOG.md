# Changelog

## 4.0.4 (2018/09/24)

* Fix bug with Zenodo automatic export

## 4.0.3 (2018/09/24)

* Add installation documentation

## 4.0.2 (2018/09/12)

* Upgrade dependencies & fix importation issue (#292)
* Add pytest sugar script

## 4.0.1 (2018/08/09)

* Upgrade dependencies (#294) to fix importation issue (#292)

## 4.0.0 (2018/03/13)

* Add multi-pixel sets explorer
* Add dashboard with many metrics
* Add search terms highlighting
* Improve performances with large data sets
* Minor bug fixes and improvements

## 3.0.0 (2018/02/04)

* Add feature gene name to entry.description while importing database entries
* Improve error message when entries are missing
* Add admin "edit" links
* Allow to search omics units by their identifier in the admin
* Add omics units search by a ref. in the admin
* Improve UI/UX
* Add filters on pixel sets list view
* Add pixel set detail view and subset selection
* Add CSV export for pixels and pixel sets

## 2.1.0 (2018/01/22)

* Fix SGD/CGD data import
* Add explorer view for Pixel sets

## 2.0.0 (2018/01/19)

* Add full-featured data importation workflow
* Add support for analysis & experiment tagging during submission
* Allow to import SGD data
* Various improvements to make Pixel's admin more user-friendly
* Minor UI improvements

## 1.2.1 (2017/12/22)

* Fix command to deploy to production

## 1.2.0 (2017/12/22)

* Production deployment
* Staging continuous deployment
* Add CGD chromosomal features (#104, #108, #109)
* Add importation workflow (#84, #86, #91, #92, #101, #102, #103, #104)
* Add PixelSet model (#79)
* Add checksum to importation template (#75)

## 1.1.0 (2017/11/15)

This is our very first release. It has not been tagged as `1.0.0` as it should
have been, because it took time to have a fully functional deployment strategy.

Highlighted features:

* Data modeling
* CircleCI integration
* Sass-based UI
* Fully dockerized stack
* Registered users authentication
* Importation workflow UI
