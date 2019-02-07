from __future__ import absolute_import
from __future__ import print_function
import sys
import os
import re
from collections import OrderedDict

import veriloggen as vg
import veriloggen.resolver.resolver as resolver

#-------------------------------------------------------------------------------
exclude_modules = [ 'cpr_.*' ]

target_modules = { # module_type : (port_name, port_width)
 "cpr_ram.*" :
    (('ext_addr', 'Input', vg.AnyType(name='ADDR_WIDTH')),
     ('ext_rdata', 'Output', vg.AnyType(name='DATA_WIDTH')),
     ('ext_wdata', 'Input', vg.AnyType(name='DATA_WIDTH')),
     ('ext_wvalid', 'Input', None),),
 
 "cpr_master_bus" :
    (('ext_awvalid', 'Output', vg.Int(1)),
     ('ext_awaddr', 'Output', vg.AnyType(name='ADDR_WIDTH')),
     ('ext_awlen', 'Output', vg.Int(8)),
     ('ext_awready', 'Input', vg.Int(1)),
       
     ('ext_wdata', 'Output', vg.AnyType(name='DATA_WIDTH')),
     ('ext_wstrb', 'Output', vg.Divide(vg.AnyType(name='DATA_WIDTH'), vg.Int(8))),
     ('ext_wlast', 'Output', vg.Int(1)),
     ('ext_wvalid', 'Output', vg.Int(1)),
     ('ext_wready', 'Input', vg.Int(1)),
       
     ('ext_arvalid', 'Output', vg.Int(1)),
     ('ext_araddr', 'Output', vg.AnyType(name='ADDR_WIDTH')),
     ('ext_arlen', 'Output', vg.Int(8)),
     ('ext_arready', 'Input', vg.Int(1)),
     
     ('ext_rdata', 'Input', vg.AnyType(name='DATA_WIDTH')),
     ('ext_rlast', 'Input', vg.Int(1)),
     ('ext_rvalid', 'Input', vg.Int(1)),
     ('ext_rready', 'Output', vg.Int(1)),),
 
 "cpr_slave_bus" :
    (('ext_awvalid', 'Input', vg.Int(1)),
     ('ext_awaddr', 'Input', vg.AnyType(name='ADDR_WIDTH')),
     ('ext_awlen', 'Input', vg.Int(8)),
     ('ext_awready', 'Output', vg.Int(1)),
       
     ('ext_wdata', 'Input', vg.AnyType(name='DATA_WIDTH')),
     ('ext_wstrb', 'Input', vg.Divide(vg.AnyType(name='DATA_WIDTH'), vg.Int(8))),
     ('ext_wlast', 'Input', vg.Int(1)),
     ('ext_wvalid', 'Input', vg.Int(1)),
     ('ext_wready', 'Output', vg.Int(1)),
       
     ('ext_arvalid', 'Input', vg.Int(1)),
     ('ext_araddr', 'Input', vg.AnyType(name='ADDR_WIDTH')),
     ('ext_arlen', 'Input', vg.Int(8)),
     ('ext_arready', 'Output', vg.Int(1)),
     
     ('ext_rdata', 'Output', vg.AnyType(name='DATA_WIDTH')),
     ('ext_rlast', 'Output', vg.Int(1)),
     ('ext_rvalid', 'Output', vg.Int(1)),
     ('ext_rready', 'Input', vg.Int(1)),),

 "cpr_master_lite_bus" :
    (('ext_awvalid', 'Output', vg.Int(1)),
     ('ext_awaddr', 'Output', vg.AnyType(name='ADDR_WIDTH')),
     ('ext_awready', 'Input', vg.Int(1)),
     
     ('ext_wdata', 'Output', vg.AnyType(name='DATA_WIDTH')),
     ('ext_wstrb', 'Output', vg.Divide(vg.AnyType(name='DATA_WIDTH'), vg.Int(8))),
     ('ext_wvalid', 'Output', vg.Int(1)),
     ('ext_wready', 'Input', vg.Int(1)),
     
     ('ext_arvalid', 'Output', vg.Int(1)),
     ('ext_araddr', 'Output', vg.AnyType(name='ADDR_WIDTH')),
     ('ext_arready', 'Input', vg.Int(1)),
     
     ('ext_rdata', 'Input', vg.AnyType(name='DATA_WIDTH')),
     ('ext_rvalid', 'Input', vg.Int(1)),
     ('ext_rready', 'Output', vg.Int(1)),),
 
 "cpr_slave_lite_bus" :
    (('ext_awvalid', 'Input', vg.Int(1)),
     ('ext_awaddr', 'Input', vg.AnyType(name='ADDR_WIDTH')),
     ('ext_awready', 'Output', vg.Int(1)),
     
     ('ext_wdata', 'Input', vg.AnyType(name='DATA_WIDTH')),
     ('ext_wstrb', 'Input', vg.Divide(vg.AnyType(name='DATA_WIDTH'), vg.Int(8))),
     ('ext_wvalid', 'Input', vg.Int(1)),
     ('ext_wready', 'Output', vg.Int(1)),
     
     ('ext_arvalid', 'Input', vg.Int(1)),
     ('ext_araddr', 'Input', vg.AnyType(name='ADDR_WIDTH')),
     ('ext_arready', 'Output', vg.Int(1)),
     
     ('ext_rdata', 'Output', vg.AnyType(name='DATA_WIDTH')),
     ('ext_rvalid', 'Output', vg.Int(1)),
     ('ext_rready', 'Input', vg.Int(1)),),
}

#-------------------------------------------------------------------------------
reset_patterns = [ 'rst', 'reset' ]
def is_reset(s):
    for pattern in reset_patterns:
        if s.lower().count(pattern):
            return True
    return False

#-------------------------------------------------------------------------------
__tmp_count = 0
def _tmp_count():
    global __tmp_count
    ret = __tmp_count
    __tmp_count += 1
    return ret

#-------------------------------------------------------------------------------
class _Visitor(object):
    def generic_visit(self, node):
        if node is None:
            return []
        raise TypeError("Type %s is not supported." % str(type(node)))

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

#-------------------------------------------------------------------------------
class RegVisitor(_Visitor):
    def visit_tuple(self, node):
        ret = []
        for n in node:
            ret.extend(self.visit(n))
        return ret

    def visit_list(self, node):
        return self.visit_tuple(node)

    def visit_If(self, node):
        ret = []
        ret.extend(self.visit(node.true_statement))
        ret.extend(self.visit(node.false_statement))
        return ret

    def visit_Case(self, node):
        ret = []
        for s in node.statement:
            ret.extend(self.visit(s))
        return ret

    def visit_When(self, node):
        ret = []
        for s in node.statement:
            ret.extend(self.visit(s))
        return ret

    def visit_For(self, node):
        ret = []
        for s in node.statement:
            ret.extend(self.visit(s))
        return ret

    def visit_While(self, node):
        ret = []
        for s in node.statement:
            ret.extend(self.visit(s))
        return ret

    def visit_Subst(self, node):
        left = self.visit(node.left)
        return left

    def visit_Reg(self, node):
        return [ node ]

    def visit_Cat(self, node):
        ret = []
        for var in node.vars:
            ret.extend(self.visit(var))
        return ret

    def visit_Pointer(self, node):
        return [ node ]

    def visit_Slice(self, node):
        return [ node ]

    def visit_Scope(self, node):
        raise NotImplementedError("Type 'Scope' is not supported.")

    @staticmethod
    def _get_variable_name(obj):
        if isinstance(obj, vg.Pointer) or isinstance(obj, vg.Slice):
            return RegVisitor._get_variable_name(obj.var)

        if hasattr(obj, 'name'):
            return obj.name

        raise TypeError("Not supported type '%s'" % str(type(obj)))

    @staticmethod
    def _to_variable_dict(regs):
        ret = OrderedDict()

        for reg in regs:
            name = RegVisitor._get_variable_name(reg)
            if name in ret:
                continue

            ret[name] = reg

        return ret

#-------------------------------------------------------------------------------
class ModuleConverter(object):
    def __init__(self, ctrl='cpr_ctrl_', signal='cpr_', module_dict=None):
        self.ctrl = ctrl
        self.signal = signal
        self.module_dict = {} if module_dict is None else module_dict
        
        self.ctrl_read = None
        self.ctrl_write = None

        self.read_ports = OrderedDict()
        self.write_ports = OrderedDict()
        self.target_ports = OrderedDict()

    #---------------------------------------------------------------------------
    def convert_module(self, m):
        self.module_dict[m.name] = m
        self.insert_control_port(m)
        self.insert_port(m)
        self.modify_always(m)
        self.insert_submod_port(m)

    def convert(self, m):
        if not isinstance(m, vg.Module):
            raise TypeError("'convert' method requires veriloggen.Module object, not %s" %
                            str(type(m)))
    
        self.convert_module(m)
        return m

    #---------------------------------------------------------------------------
    def _read_name(self, obj):
        return self.signal + 'read_' + obj.name

    def _write_name(self, obj):
        return self.signal + 'write_' + obj.name

    def get_write_port(self, obj):
        name = self._write_name(obj)
        port = self.write_ports[name]
        return port

    def _add_read_port(self, m, reg):
        rname = self._read_name(reg)
        r = m.OutputLike(reg, name=rname)
        r.assign(reg)
        self.read_ports[rname] = r
        return r

    def _add_write_port(self, m, reg):
        wname = self._write_name(reg)
        w = m.InputLike(reg, name=wname)
        self.write_ports[wname] = w
        return w
    
    #---------------------------------------------------------------------------
    def insert_control_port(self, m):
        # control port
        self.ctrl_read = m.Input(self.ctrl + 'read')
        self.ctrl_write = m.Input(self.ctrl + 'write')
    
    #---------------------------------------------------------------------------
    def insert_submod_port(self, m):
        # sub-module
        for instname, inst in m.instance.items():

            # target module
            for modname, signals in target_modules.items():
                matched = re.match(modname, inst.module.name)
                if matched:
                    self._insert_submod_port_target_module(m, instname, inst, modname, signals)

            # exclude module check
            skip_this_module = False
            
            for em in exclude_modules:
                matched = re.match(em, inst.module.name)
                if matched:
                    skip_this_module = True

            if skip_this_module:
                continue

            # normal module 
            self._insert_submod_port_normal_module(m, instname, inst)

    def _insert_submod_port_target_module(self, m, instname, inst, modname, signals):
        const_dict = OrderedDict()
        for k, v in inst.params:
            const_dict[k] = v
            
        cvisitor = resolver.ConstantVisitor(const_dict)
        
        ports = []
        ports.append( (self.ctrl + 'read', self.ctrl_read) )
        ports.append( (self.ctrl + 'write', self.ctrl_write) )
        
        for name, _type, width in signals:
            method = getattr(m, _type)
            pwidth = cvisitor.visit(width)
            pname = ''.join((self.signal, 'targ_', instname, '_', name))
            v = method(name=pname, width=pwidth)
            self.target_ports[pname] = v
            ports.append( (name, v) )
            
        inst.ports.extend(ports)
        
    def _insert_submod_port_normal_module(self, m, instname, inst):
        submod = inst.module
        converter = ModuleConverter(self.ctrl, self.signal)
        submod = converter.convert(submod)

        ports = []
        ports.append( (self.ctrl + 'read', self.ctrl_read) )
        ports.append( (self.ctrl + 'write', self.ctrl_write) )
        
        for sub_rname, sub_r in converter.read_ports.items():
            rname = sub_rname.replace(self.signal + 'read_',
                                      ''.join((self.signal, 'read_', instname, '_')), 1)
            r = m.OutputLike(sub_r, name=rname)
            self.read_ports[rname] = r
            ports.append( (sub_rname, r) ) 
            
        for sub_wname, sub_w in converter.write_ports.items():
            wname = sub_wname.replace(self.signal + 'write_',
                                      ''.join((self.signal, 'write_', instname, '_')), 1)
            w = m.OutputLike(sub_w, name=wname)
            self.write_ports[wname] = w
            ports.append( (sub_wname, w) )

        for sub_tname, sub_t in converter.target_ports.items():
            tname = sub_tname.replace(self.signal + 'targ_',
                                      ''.join((self.signal, 'targ_', instname, '_')), 1)
            if isinstance(sub_t, vg.Input):
                t = m.InputLike(sub_t, name=tname)
            elif isinstance(sub_t, vg.Output):
                t = m.OutputLike(sub_t, name=tname)
            self.target_ports[tname] = t
            ports.append( (sub_tname, t) )

        inst.ports.extend(ports)
            
    #---------------------------------------------------------------------------
    def insert_port(self, m):
        for alw in m.always:
            self._insert_read_port(m, alw)
        for alw in m.always:
            self._insert_write_port(m, alw) 

    def _insert_read_port(self, m, alw):
        if not alw.sensitivity: # comb
            return

        for s in alw.sensitivity:
            if not isinstance(s, (vg.Posedge, vg.Negedge)):
                return
                    
        reg_visitor = RegVisitor()
        for st in alw.statement:
            regs = RegVisitor._to_variable_dict(reg_visitor.visit(st))
            for reg in regs.values():
                self._add_read_port(m, reg)

    def _insert_write_port(self, m, alw):
        if not alw.sensitivity: # comb
            return

        for s in alw.sensitivity:
            if not isinstance(s, (vg.Posedge, vg.Negedge)):
                return
                    
        reg_visitor = RegVisitor()
        for st in alw.statement:
            regs = RegVisitor._to_variable_dict(reg_visitor.visit(st))
            for reg in regs.values():
                self._add_write_port(m, reg)

    #---------------------------------------------------------------------------
    def modify_always(self, m):
        new_always = [ self._modify_always_obj(m, alw) for alw in m.always ]
        m.always = new_always

    def _modify_always_obj(self, m, alw):
        if not alw.sensitivity: # comb
            return alw

        for s in alw.sensitivity:
            if not isinstance(s, (vg.Posedge, vg.Negedge)):
                return alw
                    
        new_statement = []
        reg_visitor = RegVisitor()
    
        for st in alw.statement:
            regs = RegVisitor._to_variable_dict(reg_visitor.visit(st))
            st = self._modify_always_statement(m, st, regs)
            new_statement.append(st)
                
        alw.statement = new_statement
        return alw

    def _modify_always_statement(self, m, st, regs):
        if (isinstance(st, vg.If) and
            hasattr(st.condition, 'name') and
            is_reset(st.condition.name)): # reset case
            st.false_statement = self._modify_always_statement_body(m, st.false_statement, regs)
        else: # no reset case
            st = self._modify_always_statement_body(m, st, regs)
    
        return st

    def _modify_always_statement_body(self, m, st, regs):
        write_body = []
        
        for reg in regs.values():
            wport = self.get_write_port(reg)
            write_body.append( reg(wport) )

        write = vg.If(self.ctrl_write)( *write_body )
        main = write.Else(vg.If(vg.Not(self.ctrl_read))(st))

        return main

#-------------------------------------------------------------------------------
def convert(m, ctrl='cpr_ctrl_', signal='cpr_'):
    converter = ModuleConverter(ctrl, signal)
    m = resolver.resolve(m)
    m = converter.convert(m)
    return m

def convert_from_file(topmodule, *filelist, **opt):
    modules = vg.from_verilog.read_verilog_module(*filelist, **opt)
    m = modules[topmodule]
    return convert(m)
