Vue.component('autocomplete', {
    template: '<input :value="value" @input="updateText"/>',
    props: ['url', 'value'],
    mounted: function() {
        var self = this;
        $(this.$el).autocomplete({
            source: function(request, response) {
                axios.get(self.url, {params: {search: request.term}})
                .then(function(rest_response) {
                    response($.map(rest_response.data, function(item) {
                        return {label: item.name};
                    }));
                });
            },
            select: function (event, ui) {
                self.$el.value = ui.item.label;
                self.updateText();
                return false;
            }
        });
    },
    methods: {
        updateText: function() {
            this.$emit('input', this.$el.value);
        }
    }
});

var app = new Vue({
    el: '#app',
    data: {
        uid: null,
        mode: 'start',
        question_id: null,
        question: null,
        guess_id: null,
        guess: null,
        second_guess_id: null,
        second_guess: null,
    },
    methods: {
        start: function() {
            var self = this;
            axios.post('/play/', {})
            .then(function(response) {
                self.uid = response.data.uid;
                self.next(response);
            });
        },
        answer: function(choice) {
            var self_next = this.next.bind(this);
            axios.post('/play/', {uid: this.uid, question_id: this.question_id, choice: choice})
            .then(self_next);
        },
        answer_guess: function(choice) {
            var self_next = this.next.bind(this);
            axios.post('/play/', {uid: this.uid, guess_id: this.guess_id, choice: choice})
            .then(self_next);
        },
        send_guess: function() {
            var self_next = this.next.bind(this);
            axios.post('/play/', {uid: this.uid, guess: this.guess})
            .then(self_next);
        },
        send_question: function() {
            var self_next = this.next.bind(this);
            axios.post('/play/', {uid: this.uid, question: this.question, second_guess_id: this.second_guess_id})
            .then(self_next);
        },
        next: function(response) {
            if ('question' in response.data) {
                this.question_id = response.data.question_id;
                this.question = response.data.question;
                this.mode = 'question';
            } else if ('guess' in response.data) {
                this.guess_id = response.data.guess_id;
                this.guess = response.data.guess;
                this.mode = 'guess';
            } else if ('send_guess' in response.data) {
                this.guess = null;
                this.mode = 'send_guess';
            } else if ('send_question' in response.data) {
                this.question = null;
                this.second_guess_id = response.data.second_guess_id;
                this.second_guess = response.data.second_guess;
                this.mode = 'send_question';
            } else if ('finish' in response.data) {
                this.mode = 'continue';
            }
        },
    }
});
