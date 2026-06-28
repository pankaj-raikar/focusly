import fixture from "../fixtures/binary-search.json";
import {describe, expect, it} from "vitest";
import {lessonSchema} from "../src/lesson";
import {getSceneLayout} from "../src/scenes";

describe("scene layouts", () => {
  it("maps every supported visual type to trusted display data", () => {
    const lesson = lessonSchema.parse(fixture);

    expect(lesson.segments.map(getSceneLayout)).toEqual([
      {
        kind: "title",
        eyebrow: "A faster way to search",
        title: "The guessing shortcut",
      },
      {
        kind: "bullets",
        items: ["Sorted values", "Check the middle", "Keep only the possible half"],
        title: "Start with sorted data",
      },
      {
        kind: "comparison",
        left: ["Discard", "1  3  5"],
        right: ["Keep", "9  11  13"],
        title: "Compare once",
      },
      {
        kind: "steps",
        items: ["Choose middle", "Compare target", "Discard half"],
        title: "Repeat on the smaller range",
      },
      {
        kind: "diagram",
        nodes: ["16 items", "8 items", "4 items", "2 items", "Found"],
        title: "Half, then half again",
      },
    ]);
  });
});
