odoo.define('ceylex_dashboard.dashboard', function (require) {
"use strict";
var core = require('web.core');
var rpc = require('web.rpc');
var ajax = require('web.ajax');
var AbstractAction = require('web.AbstractAction');
var QWeb = core.qweb;

var ceylexDashboardWidget = AbstractAction.extend({
    template: "CeyDashboard",
    events:{
        'click .profit_and_loss': 'action_profit_and_loss',
        'click .aged_receivable': 'action_aged_receivable',
        'click .cash_flow_statement': 'action_cash_flow_statement',
        'click .executive_summery': 'action_executive_summery',
        'click #btnSearch': function(e){
            var self = this;
            this.start_date = $("#inputStartDate").val();
            this.end_date = $("#inputEndDate").val();
            Promise.resolve(this.fetch_data()).then(function () {
                self.$('.o_ceylex_dashboard').empty();
                self.render_dashboards();
            });
        }
    },

    init: function(parent, context) {
        this._super(parent, context);

        this.dashboards_templates = ['MainDashboard', 'InvoiceReportMenu', 'EnergyDelivered'];
        this.energy_delivered = [];
        this.power_generations_summery = [];
        this.start_date ;
        this.end_date;
        this.financial_report_id;
        this.executive_summery_id;

//

    },

    willStart: function(){
        var self = this;

        return $.when(ajax.loadLibs(this), this._super()).then(function(){
            return self.fetch_data();
        });
    },


    start: function() {
        var self = this;
        this.set("title", 'Dashboard');
        return this._super().then(function() {
            self.render_dashboards();
        });
    },

    render_dashboards: function() {
        var self = this;
        _.each(this.dashboards_templates, function(template) {
            self.$('.o_ceylex_dashboard').append(QWeb.render(template, {widget: self}));
        });
    },

    fetch_data: function() {
            var self = this;
            var date = new Date();
            // get first date in this month
            var firstDay = new Date(date.getFullYear(), date.getMonth(), 1);
            var firstdate = firstDay.getDate();
            var firstmonth = firstDay.getMonth() + 1;
            var firstyear = firstDay.getFullYear();

            if (firstmonth < 10) firstmonth = "0" + firstmonth;
            if (firstdate < 10) firstdate = "0" + firstdate;
            var firstDay = firstyear + "-" + firstmonth + "-" + firstdate;
            self.start_date = self.start_date ? self.start_date: firstDay;

            // get last date in this month
            var lastDay = new Date(date.getFullYear(), date.getMonth() + 1, 0);
            var lastdate = lastDay.getDate();
            var lastmonth = lastDay.getMonth() + 1;
            var lastyear = lastDay.getFullYear();

            if (lastmonth < 10) lastmonth = "0" + lastmonth;
            if (lastdate < 10) lastdate = "0" + lastdate;
            var lastDay = lastyear + "-" + lastmonth + "-" + lastdate;

            self.end_date = self.end_date ? self.end_date: lastDay;

            var energy = self._rpc({
                model: "account.move",
                method: "get_energy_delivered_to_national_grid",
                args: [self.start_date, self.end_date]
            })
            .then(function (res) {
                self.energy_delivered = res['energy'];
            });

            var power = self._rpc({
                model: "energy.calculation",
                method: "get_power_generated_summery",
                args: [self.start_date, self.end_date]
            })
            .then(function (res) {
                self.power_generations_summery = res['power'];
            });

            var financial_report_ids = self._rpc({
                model: "ir.model.data",
                method: "check_object_reference",
                args: ['account_reports', 'account_financial_report_profitandloss0']
            })
            .then(function (res) {
                self.financial_report_id = res[1];
            });

            var executive_summery_ids = self._rpc({
                model: "ir.model.data",
                method: "check_object_reference",
                args: ['account_reports', 'account_financial_report_executivesummary0']
            })
            .then(function (res) {
                self.executive_summery_id = res[1];
            });





                console.log(self.start_date);


            return $.when(energy, power, financial_report_ids, executive_summery_ids,);
    },


    action_profit_and_loss: function(){
    //Load profit and loss report
        this.do_action({
            type: 'ir.actions.client',
            name: 'Profit And Loss',
            tag: 'account_report',
            target: 'current',
            context: {
                model: 'account.financial.html.report',
                id: this.financial_report_id
            },
        });
    },


    action_aged_receivable: function(){
        this.do_action({
            type: 'ir.actions.client',
            name: 'Aged Receivable',
            tag: 'account_report',
            target: 'current',
            context: {
                model: 'account.aged.receivable'},
        });
    },

    action_cash_flow_statement: function(){
        this.do_action({
            type: 'ir.actions.client',
            name: 'Cash Flow Statement',
            tag: 'account_report',
            target: 'current',
            context: {
                model: 'account.cash.flow.report',
            },
        });
    },
    action_executive_summery: function(){
        this.do_action({
            type: 'ir.actions.client',
            name: 'Executive Summary',
            tag: 'account_report',
            target: 'current',
            context: {
                model: 'account.financial.html.report',
                id: this.executive_summery_id
            },
        });
    },


});

core.action_registry.add('ceylex_dashboard', ceylexDashboardWidget);

return ceylexDashboardWidget;


});