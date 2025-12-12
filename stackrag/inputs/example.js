// Top-level function declaration
function add(a, b) {
    return a + b;
}

// Top-level arrow function
const multiply = (x, y) => x * y;

// Function expression
const divide = function(a, b) {
    return a / b;
};

// Variable statement
let count = 10;

// Loop statement
for (let i = 0; i < count; i++) {
    console.log(i);
}

// Object with a method
const obj = {
    greet() {
        console.log("Hello!");
    }
};

// Class with a method
class MyClass {
    sayHi() {
        console.log("Hi from class!");
    }
}

// IIFE
(function() {
    console.log("IIFE running");
})();