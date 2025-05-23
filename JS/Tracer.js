"use strict";

const { FuncID, FuncStack } = require('./FuncStack');
const os = require('os');
const fs = require('fs');
const path = require('path');

class Tracer {
	constructor(config, isBase) {
		this.config = config;
		this.baseFuncStack = new FuncStack("ENTRY_POINT"); 
		this.currentPath = ""; // relative path to the git root folder
		this.currentFuncStack = this.baseFuncStack; // type: FuncStack
		this.isBase = isBase;
	}

	static buildFuncStack(filePath, funcPath, hash) {
		const funcID = new FuncID(filePath, funcPath, hash);
		return new FuncStack(funcID);
	}

	push(funcStack) {
		if (this.currentFuncStack === null)
			throw new Error("Tracer uninitialized!");

		this.currentFuncStack.pushCallee(funcStack); // pushCallee() will update id and index immediately
	}

	move(funcStack) { this.currentFuncStack = funcStack; }
	
	moveTop() { 
		if (this.currentFuncStack.index.length <= 0)
			throw new Error("Reach highest call stack, can't move top.");

		this.currentFuncStack = FuncStack.getFuncStack(this.baseFuncStack, this.currentFuncStack.index.slice(0, this.currentFuncStack.index.length - 1)); 
	}

	writeFuncStacks() {
		const callGraph = JSON.stringify(global.BugbeeTracer.baseFuncStack, null, 2);
		const projectName = path.basename(this.config.sourceFolder) + "_" + ((this.isBase) ? "base" : "new");
		const fsPath = path.join(os.homedir(), this.config.generateFolder, "trace", projectName, projectName + ".json");
		fs.writeFileSync(fsPath, callGraph);
	}
}
module.exports._Tracer_ = Tracer;

if (global.BugbeeTracer === undefined) {
	global.BugbeeTracer = new Tracer(JSON.parse(process.env.BugbeeConfig), process.env.isBugbeeBase === 'true');
	process.on('exit', () => {
		global.BugbeeTracer.writeFuncStacks();
	});
}
