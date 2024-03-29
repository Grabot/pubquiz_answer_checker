angular.module('requestsModule', [])
    .factory('httpRequestsService', function($http){
        return{
            getQuestions: function (){
                return  $http({
                    method: "GET",
                    url: "/api/v1.0/questions"
                })
            },
            getTeams: function(){
                return $http({
                    method: "GET",
                    url: "/api/v1.0/teams"
                })
            },
            getCategories: function(){
                return $http({
                    method: "GET",
                    url: "/api/v1.0/categories"
                })
            },
            getAnswers: function (team, category, question, correct, checkedby, confidenceFrom, confidenceTo) {
                var url = new URL('/api/v1.0/answers', window.location.origin);
                if(team != null){
                    url.searchParams.append('team_id', team.id);
                }
                if(category != null){
                    url.searchParams.append('category_id', category.id);
                }
                if(question != null){
                    url.searchParams.append('question_id', question.id);
                }
                if(correct != null){
                    url.searchParams.append('correct', correct);
                }
                if(checkedby != null){
                    url.searchParams.append('checkedby_id', checkedby.id);
                }
                if(confidenceFrom != null){
                    url.searchParams.append('confidence_from', confidenceFrom);
                }
                if(confidenceTo != null){
                    url.searchParams.append('confidence_to', confidenceTo);
                }
                let response = $http.get(url.toString());
                return response;
            },
            getPersons: function(){
                 return $http({
                    method: "GET",
                    url: "/api/v1.0/persons"
                })
            },

            addQuestion: function(question){
                 return $http.post("/api/v1.0/newquestion", question)
            },

            removeQuestion: function(question){
                 return $http.post("/api/v1.0/removequestion", question)
            },

            deleteAllQuestions: function(){
                return $http.post("/api/v1.0/deleteallquestions")
            },

            updateQuestion: function(question){
                return $http.post("/api/v1.0/updatequestion", question)
            },

            resetQuestionNumbers: function(){
                $http.post("/api/v1.0/resetquestionnumbers")
            },

            deleteCategory: function(category){
                return $http.post("/api/v1.0/removecategory", category)
            },

            createDoc: function(document){
                return $http.post("/api/v1.0/createdoc", document)
            },

            addTeam: function(team){
                return $http.post("/api/v1.0/newteam", team)
            },

            removeTeam: function(team){
                $http.post("/api/v1.0/removeteam", team)
            },

            updateTeam: function(team){
                $http.post("/api/v1.0/updateteam", team)
            },

            checkAnswers: function(){
                return $http.post("/api/v1.0/checkanswers")
            },

            updateAnswer: function(answer){
                return $http.post("/api/v1.0/updateanswer", answer)
            },

            deleteAllAnswers: function(){
                $http.post("/api/v1.0/reset")
            }
        }
    })
