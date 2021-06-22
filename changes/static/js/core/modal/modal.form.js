'use strict';

angular.module('core.modalForm', ['ui.bootstrap'])
.factory('formService', ['$uibModal', '$log', function ($uibModal, $log) {

  var ModalInstanceCtrl = function($scope, $http, $window, $timeout, $uibModalInstance, config) {

    $scope.sync = false;
    $scope.error = '';
    $scope.formInvalid = false;
    $scope.data = config.field?config.data[config.field]:config.data;

    $scope.ok = function (f) {

      // form input invalid
      if (f.$invalid) {
        $scope.formInvalid = true;
        return;
      }

      if (config.path) {
        $scope.sync = true;
        $scope.error = '';
        $scope.succ = false;
        $http({
          method: config.method || 'POST',
          url: config.path,
          data: $scope.data
        }).then(function(data, status, headers, cfg) {
          if (data.data.is_success) {
            $scope.success = data.data.message;
            $timeout(function() { $scope.succ = true;}, 3000);
            if (config.redirect) {
              $window.location.hash = "";
              $timeout(function() {
                $window.location.pathname = config.redirect;
              }, 2900);
            } else {
              if (config.callback) {
                config.callback(config.data, data);
              }

              if (config.closeOnSuccess) {
                return $uibModalInstance.close();
              }
              $scope.succ = true;
              $scope.sync = false;
            }
          } else {
            $scope.sync = false;
            $scope.error = data.data.message;
            $timeout(function() { $scope.error = '';}, 5000);
          }

        }).catch(function(error, response) {
          $scope.sync = false;
          $scope.error = response.data.message || 'server response:' + response.status;
          $timeout(function() { $scope.error = '';}, 5000);
        });
      } else {
        if (config.callback) {
          config.callback(config.data, null);
        }

        if (config.closeOnSuccess) {
          $uibModalInstance.close();
        }
      }
    };

    $scope.cancel = function () {
      $uibModalInstance.dismiss('cancel');
    };

  };

  var openModal = function (params) {
    // set default params
    params.data = params.data || {};
    if (!params.closeOnSuccess || params.closeOnSuccess === 'true') {
      params.closeOnSuccess = true;
    } else {
      params.closeOnSuccess = false;
    }
    params.method = params.method || 'POST';

    var modalInstance = $uibModal.open({
      templateUrl: params.templateUrl,
      controller: ModalInstanceCtrl,
      windowClass: params.dialogClass,
      resolve: {
        config: function() {
          return params;
        }
      }
    });

    modalInstance.result.then(function (data) {
      $log.info('modal closed.');
    }, function () {
      $log.info('modal dismissed.');
    });
  };

  return function(params) {
    return openModal.bind(null, params);
  };
}]).directive('modalForm', function() {
  return {
    restrict: 'EA',
    scope: {
      data: "=?", // data model bind to the modal dialog template
      field: "@", // data field that send to server
      templateUrl: "@",  // modal dialog template url, required
      method: "@",  // ajax request method, POST, PUT, etc, defaults to POST
      path: "@",   // ajax request path
      dialogClass: "@",   // same as in ui bootstrap modal
      redirect: "@",    // redirect path on success
      closeOnSuccess: "@",    // close modal on success, defaults to true
      callback: "&"   // callback function
    },
    controller: ['$scope', 'formService', function($scope, formService) {
      $scope.open = formService($scope);
    }],
    link: function(scope, element, attrs) {
      element.click(function() {scope.open();});
    }
  };
});