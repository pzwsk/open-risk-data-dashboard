/**
 * Created by Manuel on 15/05/2017.
 */

var RodiApp = angular.module('RodiApp', ['ngCookies', 'ngTable']);

// var baseUrl = 'http://localhost:63342/open-risk-data-dashboard/frontend/';
function getLocation(href) {
    var match = href.match(/^(https?\:)\/\/(([^:\/?#]*)(?:\:([0-9]+))?)([\/]{0,1}[^?#]*)(\?[^#]*|)(#.*|)$/);
    return match && {
        href: href,
        protocol: match[1],
        host: match[2],
        hostname: match[3],
        port: match[4],
        pathname: match[5],
        search: match[6],
        hash: match[7]
    }
}

var spli_url = getLocation(window.location.href);
// var baseUrl = 'https://www.riskopendata.org/';
//var baseUrl = spli_url.protocol + '//' + spli_url.host + '/';
var baseUrl = 'http://localhost/open-risk-data-dashboard/frontend/';

var baseAPIurl = 'https://www.riskopendata.org/api/'; // Sviluppo
//var baseAPIurl = spli_url.protocol + '//' + spli_url.host + '/api/';
var APIversion = '0.27.0';

RodiApp.config(function($locationProvider) {

    $locationProvider.html5Mode(true);

});
