// Setup
// -----------------------------------------------------------------------------

// Base
const {series, watch, src, dest, parallel} = require("gulp");
const pump = require("pump");
const path = require("path");
const inquirer = require("inquirer");

// Gulp plugins and utils
const livereload = require("gulp-livereload");
const postcss = require("gulp-postcss");
const zip = require("gulp-zip");
const concat = require("gulp-concat");
const uglify = require("gulp-uglify");
const beeper = require("beeper");
const fs = require("fs");
const sass = require("gulp-sass");

// Postcss plugins
const autoprefixer = require("autoprefixer");
const cssnano = require("cssnano");
const easyimport = require("postcss-easy-import");

// Tasks
// -----------------------------------------------------------------------------

function serve(done) {
  livereload.listen();
  done();
}

const handleError = (done) => {
  return function (err) {
    if (err) {
      beeper();
    }
    return done(err);
  };
};

function hbs(done) {
  pump([
    src(["*.hbs", "partials/**/*.hbs"]),
    livereload()
  ], handleError(done));
}

function styles(done) {
  pump([
    src("assets/stylesheets/bb.scss", {sourcemaps: true}),
    sass(),
    postcss([
      easyimport,
      autoprefixer(),
      cssnano()
    ]),
    dest("assets/", {sourcemaps: "."}),
    livereload()
  ], handleError(done));
}

function js(done) {
  pump([
    src([
      "assets/js/lib/*.js",
      "assets/js/*.js"
    ], {sourcemaps: true}),
    concat("bb.js"),
    uglify(),
    dest("assets/", {sourcemaps: "."}),
    livereload()
  ], handleError(done));
}

function zipper(done) {
  const filename = require("./package.json").name + ".zip";
  pump([
    src([
      "**",
      "!node_modules", "!node_modules/**",
      "!dist", "!dist/**",
      "!yarn-error.log",
      "!yarn.lock",
      "!gulpfile.js",
      "!assets/js", "!assets/js/**",
      "!assets/stylesheets", "!assets/stylesheets/**",
    ]),
    zip(filename),
    dest("dist/")
  ], handleError(done));
}

// CLI Exports
// -----------------------------------------------------------------------------

const cssWatcher = () => watch("assets/stylesheets/**", styles);
const jsWatcher = () => watch("assets/js/**", js);
const hbsWatcher = () => watch(["*.hbs", "partials/**/*.hbs"], hbs);
const watcher = parallel(cssWatcher, jsWatcher, hbsWatcher);
const build = series(styles, js);

exports.build = build;
exports.zip = series(build, zipper);
exports.default = series(build, serve, watcher);
