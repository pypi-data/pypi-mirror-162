# -*- coding: utf-8 -*-
"""
Created on Mon Dec 20 13:19:38 2021
@author: ninad
"""
import Rotors
import cipher
import generate
import convert

class EnigmaOP:
    
    def __init__(self):
        self.tple=Rotors.Rotor()
        self.wiring=list(self.tple)

    
        self.input_string=''
        self.copyinput=self.input_string
        self.cipher_text=''
        self.initialsettings=[]
        self.plugboard={}

        self.level =3

        self.Rotor_combination,self.Rotor_Setting,self.plugboard=generate.random_settings()
        self.initialsettings.append(self.Rotor_combination)
        self.initialsettings.append(tuple(self.Rotor_Setting))
        self.initialsettings.append(self.plugboard)
    
    def encrypt(self,input_string):
        for i in input_string:
    
            self.ascii_num=convert.tonum(i)
    
            self.Rotor_combination,self.Rotor_Setting,self.ascii_num=cipher.encrypt(self.Rotor_combination,self.Rotor_Setting,self.plugboard,self.ascii_num,self.level)
            self.var=self.ascii_num
    
            self.cipher_text=self.cipher_text+convert.tochar(self.var)
        return self.cipher_text