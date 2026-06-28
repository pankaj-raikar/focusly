import fixture from "../fixtures/binary-search.json";
import {describe, expect, it} from "vitest";
import {
  FPS,
  getDurationInFrames,
  getSceneStartFrames,
  lessonSchema,
} from "../src/lesson";

describe("lesson timeline", () => {
  it("validates the fixture and totals segment durations", () => {
    const lesson = lessonSchema.parse(fixture);

    expect(lesson.segments).toHaveLength(5);
    expect(getDurationInFrames(lesson)).toBe(20 * FPS);
    expect(getSceneStartFrames(lesson)).toEqual([0, 120, 240, 360, 480]);
  });

  it("rejects an unsupported scene type", () => {
    const invalid = structuredClone(fixture);
    invalid.segments[0]!.visualType = "generated-code";

    expect(() => lessonSchema.parse(invalid)).toThrow();
  });

  it("accepts null fields emitted by the Python structured-output schema", () => {
    const lesson = {
      ...fixture,
      segments: fixture.segments.map((segment, index) =>
        index === 0
          ? {
              ...segment,
              visualPayload: {
                eyebrow: "A faster way to search",
                items: null,
                leftLabel: null,
                leftValue: null,
                rightLabel: null,
                rightValue: null,
                nodes: null,
              },
            }
          : segment,
      ),
    };

    expect(lessonSchema.parse(lesson).segments[0]!.visualType).toBe("title");
  });

  it("converts fractional audio seconds into whole render frames", () => {
    const lesson = {
      ...fixture,
      segments: fixture.segments.map((segment, index) => ({
        ...segment,
        targetSeconds: index === 0 ? 3.175 : 1,
      })),
    };

    const parsed = lessonSchema.parse(lesson);
    expect(getSceneStartFrames(parsed)).toEqual([0, 96, 126, 156, 186]);
    expect(getDurationInFrames(parsed)).toBe(216);
  });
});
