// module and controller in the module
(function () {
    var app = angular.module('work', ['ngRoute']);                         // 모듈 정의 함수, 모듈 이름 - project

    app.controller('WorkCtrl', [ '$scope', function($scope){     // $scope - html, js 연결고리
        $scope.worktodo = [{
            title: 'Delivery',
            job: '111'
        },{
            title: 'Products',
            job: '222'
        }];

        $scope.remove = function (work) {                            // ng-click='remove()'
            // find the project data from projects
            var idx = $scope.worktodo.findIndex(function (item)     // idx = index
            { return item.id == work.id;                         // item은 저장된 project, project는 html 에서 선택된 project
            })

            // remove the project
            if (idx > -1) {                         // 존재할시 -1보다 크므로
                $scope.worktodo.splice(idx, 1)}
        };

        $scope.add = function (title, job) {     // 3개 변수
        // create a new project
            var newWork = {
                title: title,
                job: job
            };

            $scope.worktodo.push(newWork);
            $scope.title = "";
            $scope.job = "";

        //}
        }}]);

    app.config(['$interpolateProvider', function($interpolateProvider) {   //   flask jinja2
      $interpolateProvider.startSymbol('//');
      $interpolateProvider.endSymbol('//');
    }]);

}
) ();   // 함수 끝에 ()
