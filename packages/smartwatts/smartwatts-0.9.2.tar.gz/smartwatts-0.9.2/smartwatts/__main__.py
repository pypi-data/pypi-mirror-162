# Copyright (c) 2022, INRIA
# Copyright (c) 2022, University of Lille
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import logging
import signal
import sys
from typing import Dict

from powerapi import __version__ as powerapi_version
from powerapi.dispatcher import RouteTable

from powerapi.cli import ConfigValidator
from powerapi.cli.tools import store_true, CommonCLIParser
from powerapi.cli.generator import ReportModifierGenerator, PullerGenerator, PusherGenerator
from powerapi.message import DispatcherStartMessage
from powerapi.report import HWPCReport, PowerReport
from powerapi.dispatch_rule import HWPCDispatchRule, HWPCDepthLevel
from powerapi.filter import Filter
from powerapi.actor import InitializationException, PowerAPIException
from powerapi.supervisor import Supervisor

from smartwatts import __version__ as smartwatts_version
from smartwatts.report import FormulaReport
from smartwatts.dispatcher import SmartwattsDispatcherActor
from smartwatts.actor import SmartWattsFormulaActor, SmartwattsValues
from smartwatts.context import SmartWattsFormulaScope, SmartWattsFormulaConfig
from smartwatts.topology import CPUTopology


def generate_smartwatts_parser():
    """
    Construct and returns the SmartWatts cli parameters parser.
    :return: SmartWatts cli parameters parser
    """
    parser = CommonCLIParser()

    # Formula control parameters
    parser.add_argument('disable-cpu-formula', help='Disable CPU formula', flag=True, type=bool, default=False, action=store_true)
    parser.add_argument('disable-dram-formula', help='Disable DRAM formula', flag=True, type=bool, default=False, action=store_true)

    # Formula RAPL reference event
    parser.add_argument('cpu-rapl-ref-event', help='RAPL event used as reference for the CPU power models', default='RAPL_ENERGY_PKG')
    parser.add_argument('dram-rapl-ref-event', help='RAPL event used as reference for the DRAM power models', default='RAPL_ENERGY_DRAM')

    # CPU topology information
    parser.add_argument('cpu-tdp', help='CPU TDP (in Watt)', type=int, default=125)
    parser.add_argument('cpu-base-clock', help='CPU base clock (in MHz)', type=int, default=100)
    parser.add_argument('cpu-frequency-min', help='CPU minimal frequency (in MHz)', type=int, default=100)
    parser.add_argument('cpu-frequency-base', help='CPU base frequency (in MHz)', type=int, default=2300)
    parser.add_argument('cpu-frequency-max', help='CPU maximal frequency (In MHz, with Turbo-Boost)', type=int, default=4000)

    # Formula error threshold
    parser.add_argument('cpu-error-threshold', help='Error threshold for the CPU power models (in Watt)', type=float, default=2.0)
    parser.add_argument('dram-error-threshold', help='Error threshold for the DRAM power models (in Watt)', type=float, default=2.0)

    # Sensor information
    parser.add_argument('sensor-report-sampling-interval', help='The frequency with which measurements are made (in milliseconds)', type=int, default=1000)

    # Learning parameters
    parser.add_argument('learn-min-samples-required', help='Minimum amount of samples required before trying to learn a power model', type=int, default=10)
    parser.add_argument('learn-history-window-size', help='Size of the history window used to keep samples to learn from', type=int, default=60)
    parser.add_argument('real-time-mode', help='Pass the wait for reports from 4 ticks to 1', type=bool, default=False)
    return parser


def filter_rule(_):
    """
    Rule of filter. Here none
    """
    return True


def setup_cpu_formula_actor(supervisor, fconf, route_table, report_filter, cpu_topology, formula_pushers, power_pushers):
    """
    Setup CPU formula actor.
    :param supervisor: Actor supervisor
    :param fconf: Global configuration
    :param route_table: Reports routing table
    :param report_filter: Reports filter
    :param cpu_topology: CPU topology information
    :param pushers: Reports pushers
    """
    formula_config = SmartWattsFormulaConfig(SmartWattsFormulaScope.CPU, fconf['sensor-report-sampling-interval'],
                                             fconf['cpu-rapl-ref-event'], fconf['cpu-error-threshold'],
                                             cpu_topology, fconf['learn-min-samples-required'],
                                             fconf['learn-history-window-size'], fconf['real-time-mode'])
    dispatcher_start_message = DispatcherStartMessage('system', 'cpu_dispatcher', SmartWattsFormulaActor,
                                                      SmartwattsValues(formula_pushers, power_pushers,
                                                                       formula_config), route_table, 'cpu')
    cpu_dispatcher = supervisor.launch(SmartwattsDispatcherActor, dispatcher_start_message)
    report_filter.filter(filter_rule, cpu_dispatcher)


def setup_dram_formula_actor(supervisor, fconf, route_table, report_filter, cpu_topology, formula_pushers, power_pushers):
    """
    Setup DRAM formula actor.
    :param supervisor: Actor supervisor
    :param fconf: Global configuration
    :param route_table: Reports routing table
    :param report_filter: Reports filter
    :param cpu_topology: CPU topology information
    :param pushers: Reports pushers
    :return: Initialized DRAM dispatcher actor
    """
    formula_config = SmartWattsFormulaConfig(SmartWattsFormulaScope.DRAM,
                                             fconf['sensor-report-sampling-interval'],
                                             fconf['dram-rapl-ref-event'],
                                             fconf['dram-error-threshold'],
                                             cpu_topology,
                                             fconf['learn-min-samples-required'],
                                             fconf['learn-history-window-size'],
                                             fconf['real-time-mode'])
    dispatcher_start_message = DispatcherStartMessage('system',
                                                      'dram_dispatcher',
                                                      SmartWattsFormulaActor,
                                                      SmartwattsValues(formula_pushers,
                                                                       power_pushers, formula_config),
                                                      route_table, 'dram')
    dram_dispatcher = supervisor.launch(SmartwattsDispatcherActor, dispatcher_start_message)
    report_filter.filter(filter_rule, dram_dispatcher)


def run_smartwatts(args) -> None:
    """
    Run PowerAPI with the SmartWatts formula.
    :param args: CLI arguments namespace
    :param logger: Logger to use for the actors
    """
    fconf = args

    logging.info('SmartWatts version %s using PowerAPI version %s', smartwatts_version, powerapi_version)

    if fconf['disable-cpu-formula'] and fconf['disable-dram-formula']:
        logging.error('You need to enable at least one formula')
        return

    route_table = RouteTable()
    route_table.dispatch_rule(HWPCReport, HWPCDispatchRule(HWPCDepthLevel.SOCKET, primary=True))

    cpu_topology = CPUTopology(fconf['cpu-tdp'], fconf['cpu-base-clock'], fconf['cpu-frequency-min'], fconf['cpu-frequency-base'], fconf['cpu-frequency-max'])

    report_filter = Filter()

    report_modifier_list = ReportModifierGenerator().generate(fconf)

    supervisor = Supervisor(args['verbose'], args['actor_system'])

    def term_handler(_, __):
        supervisor.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGTERM, term_handler)
    signal.signal(signal.SIGINT, term_handler)
    try:
        logging.info('Starting SmartWatts actors...')

        pusher_generator = PusherGenerator()
        pusher_generator.add_model_factory('FormulaReport', FormulaReport)
        pushers_info = pusher_generator.generate(args)
        pushers_formula = {}
        pushers_power = {}

        for pusher_name in pushers_info:
            pusher_cls, pusher_start_message = pushers_info[pusher_name]

            if pusher_start_message.database.report_type == PowerReport:
                pushers_power[pusher_name] = supervisor.launch(pusher_cls, pusher_start_message)
            elif pusher_start_message.database.report_type == FormulaReport:
                pushers_formula[pusher_name] = supervisor.launch(pusher_cls, pusher_start_message)
            else:
                raise InitializationException("Pusher parameters : Provide supported report type as model for pusher")

        logging.info('CPU formula is %s' % ('DISABLED' if fconf['disable-cpu-formula'] else 'ENABLED'))
        if not fconf['disable-cpu-formula']:
            logging.info('CPU formula parameters: RAPL_REF=%s ERROR_THRESHOLD=%sW' % (fconf['cpu-rapl-ref-event'], fconf['cpu-error-threshold']))
            setup_cpu_formula_actor(supervisor, fconf, route_table, report_filter, cpu_topology, pushers_formula, pushers_power)

            logging.info('DRAM formula is %s' % ('DISABLED' if fconf['disable-dram-formula'] else 'ENABLED'))
        if not fconf['disable-dram-formula']:
            logging.info('DRAM formula parameters: RAPL_REF=%s ERROR_THRESHOLD=%sW' % (fconf['dram-rapl-ref-event'], fconf['dram-error-threshold']))
            setup_dram_formula_actor(supervisor, fconf, route_table, report_filter, cpu_topology, pushers_formula, pushers_power)

        pullers_info = PullerGenerator(report_filter, report_modifier_list).generate(args)
        for puller_name in pullers_info:
            puller_cls, puller_start_message = pullers_info[puller_name]
            supervisor.launch(puller_cls, puller_start_message)
    except InitializationException as exn:
        logging.error('Actor initialization error: ' + exn.msg)
        supervisor.shutdown()
        sys.exit(-1)
    except PowerAPIException as exp:
        supervisor.shutdown()
        logging.error("PowerException Error error: %s", exp)
        sys.exit(-1)

    logging.info('SmartWatts is now running...')
    supervisor.monitor()
    logging.info('SmartWatts is shutting down...')


class SmartwattsConfigValidator(ConfigValidator):
    """
    Class used that check the config extracted and verify it conforms to constraints
    """
    @staticmethod
    def validate(config: Dict):
        if not ConfigValidator.validate(config):
            return False

        if 'disable-cpu-formula' not in config:
            config['disable-cpu-formula'] = False
        if 'disable-dram-formula' not in config:
            config['disable-dram-formula'] = False
        if 'cpu-rapl-ref-event' not in config:
            config['cpu-rapl-ref-event'] = 'RAPL_ENERGY_PKG'
        if 'dram-rapl-ref-event' not in config:
            config['dram-rapl-ref-event'] = 'RAPL_ENERGY_DRAM'
        if 'cpu-tdp' not in config:
            config['cpu-tdp'] = 125
        if 'cpu-base-clock' not in config:
            config['cpu-base-clock'] = 100
        if 'sensor-report-sampling-interval' not in config:
            config['sensor-report-sampling-interval'] = 1000
        if 'learn-min-samples-required' not in config:
            config['learn-min-samples-required'] = 10
        if 'learn-history-window-size' not in config:
            config['learn-history-window-size'] = 60
        if 'real-time-mode' not in config:
            config['real-time-mode'] = False

        # Model use frequency in 100MHz
        if 'cpu-frequency-base' in config:
            config['cpu-frequency-base'] = int(config['cpu-frequency-base'] / 100)
        if 'cpu-frequency-min' in config:
            config['cpu-frequency-min'] = int(config['cpu-frequency-min'] / 100)
        if 'cpu-frequency-max' in config:
            config['cpu-frequency-max'] = int(config['cpu-frequency-max'] / 100)

        return True


def get_config():
    """
    Get he config from the cli args
    """
    parser = generate_smartwatts_parser()
    return parser.parse()


if __name__ == "__main__":

    conf = get_config()
    if not SmartwattsConfigValidator.validate(conf):
        sys.exit(-1)
    logging.basicConfig(level=logging.WARNING if conf['verbose'] else logging.INFO)
    logging.captureWarnings(True)

    logging.debug(str(conf))
    run_smartwatts(conf)
    sys.exit(0)
