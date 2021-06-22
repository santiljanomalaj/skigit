'use strict';

// Define the `phonecatApp` module
angular.module('skigitApp', [
  'ui.bootstrap',
  'ngCookies',
  'coreSkigit',
  'userSkigit'
]).config(['$httpProvider', function ($httpProvider) {
  $httpProvider.defaults.xsrfCookieName = 'csrftoken';
  $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]);

