'use strict';

var app = angular.module('formsUpload', ['ui.validate']);

app.controller('ValidateUpload', function ($scope, $timeout, $q) {
  $scope.showsperklogo = function() {
    angular.element(document.querySelector('ul.sperk-logo')).addClass('open');
    angular.element(document.querySelector('.p_body')).css("display", "block");
  };
  $scope.pbody = function() {
    angular.element(document.querySelector('.target-div')).removeClass('open');
    angular.element(document.querySelector('ul.sperk-logo')).removeClass('open');
    angular.element(document.querySelector('.p_body')).css("display", "none");
  };
  $scope.target = function () {
    angular.element(document.querySelector('.target-div')).addClass('open');
    angular.element(document.querySelector('.p_body')).css("display", "block");
  };
  $scope.changemadeby = function () {
    $scope.ops = false;
    $scope.sorry = false;
    angular.element(document.querySelector('#id_made_by')).attr('disabled', 'disabled');
    if ($scope.changemade.length === 0 || typeof $scope.changemade === 'undefined') {
      if ($scope.add_logo === '1' || $scope.add_logo === 1) {
        $scope.ops = true;
        angular.element(document.querySelector('ul.sperk-logo')).addClass('open');
        angular.element(document.querySelector('.p_body')).css("display", "block");
      } else {
        $scope.sorry = true;
      }
    }
  }
});


  //
  // $scope.notBlackListed = function (value) {
  //   var blacklist = ['bad@domain.com', 'verybad@domain.com'];
  //   return blacklist.indexOf(value) === -1;
  // };
  // $scope.doesNotExist = function (value) {
  //   var db = ['john.doe@mail.com', 'jane.doe@mail.com'];
  //   // Simulates an asyncronous trip to the server.
  //   return $q(function (resolve, reject) {
  //     $timeout(function () {
  //       if (db.indexOf(value) < 0) {
  //         resolve();
  //       } else {
  //         reject();
  //       }
  //     }, 500);
  //   });
  // };
// });


