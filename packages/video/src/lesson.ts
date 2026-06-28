import {z} from "zod";

export const FPS = 30;

const visualPayloadSchema = z.object({
  eyebrow: z.string().nullish(),
  items: z.array(z.string()).nullish(),
  leftLabel: z.string().nullish(),
  leftValue: z.string().nullish(),
  rightLabel: z.string().nullish(),
  rightValue: z.string().nullish(),
  nodes: z.array(z.string()).nullish(),
});

export const segmentSchema = z.object({
  id: z.string().min(1),
  title: z.string().min(1),
  narration: z.string().min(1),
  visualType: z.enum(["title", "bullets", "comparison", "steps", "diagram"]),
  visualPayload: visualPayloadSchema,
  targetSeconds: z.number().positive(),
});

export const lessonSchema = z.object({
  title: z.string().min(1),
  hook: z.string().min(1),
  learningObjectives: z.array(z.string()).min(1),
  segments: z.array(segmentSchema).min(3).max(5),
  quizzes: z.array(
    z.object({
      afterSegmentId: z.string().min(1),
      question: z.string().min(1),
      options: z.array(z.string()).min(2).max(4),
      correctOptionIndex: z.number().int().nonnegative(),
      explanation: z.string().min(1),
    }),
  ),
  recap: z.array(z.string()).min(1),
  reducedMotion: z.boolean().default(false),
});

export type Lesson = z.infer<typeof lessonSchema>;
export type Segment = z.infer<typeof segmentSchema>;

export const getSegmentDurationInFrames = (segment: Segment) =>
  Math.ceil(segment.targetSeconds * FPS);

export const getDurationInFrames = (lesson: Lesson) =>
  lesson.segments.reduce(
    (frames, segment) => frames + getSegmentDurationInFrames(segment),
    0,
  );

export const getSceneStartFrames = (lesson: Lesson) => {
  let frame = 0;

  return lesson.segments.map((segment) => {
    const start = frame;
    frame += getSegmentDurationInFrames(segment);
    return start;
  });
};
