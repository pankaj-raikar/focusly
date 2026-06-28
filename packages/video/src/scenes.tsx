import type {CSSProperties, ReactNode} from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import type {Segment} from "./lesson";

type SceneLayout =
  | {kind: "title"; eyebrow: string; title: string}
  | {kind: "bullets"; items: string[]; title: string}
  | {
      kind: "comparison";
      left: [string, string];
      right: [string, string];
      title: string;
    }
  | {kind: "steps"; items: string[]; title: string}
  | {kind: "diagram"; nodes: string[]; title: string};

export const getSceneLayout = (segment: Segment): SceneLayout => {
  const payload = segment.visualPayload;

  switch (segment.visualType) {
    case "title":
      return {
        kind: "title",
        eyebrow: payload.eyebrow ?? "",
        title: segment.title,
      };
    case "bullets":
      return {kind: "bullets", items: payload.items ?? [], title: segment.title};
    case "comparison":
      return {
        kind: "comparison",
        left: [payload.leftLabel ?? "", payload.leftValue ?? ""],
        right: [payload.rightLabel ?? "", payload.rightValue ?? ""],
        title: segment.title,
      };
    case "steps":
      return {kind: "steps", items: payload.items ?? [], title: segment.title};
    case "diagram":
      return {kind: "diagram", nodes: payload.nodes ?? [], title: segment.title};
  }
};

const colors = {
  ink: "#18251f",
  muted: "#5d6d64",
  paper: "#f4f0e7",
  green: "#2f6e55",
  mint: "#d9eadf",
  coral: "#dc745c",
  white: "#fffdf8",
};

const panel: CSSProperties = {
  background: colors.white,
  border: `3px solid ${colors.ink}`,
  borderRadius: 28,
  boxShadow: `12px 12px 0 ${colors.ink}`,
};

const SceneFrame = ({
  children,
  title,
  reducedMotion,
}: {
  children: ReactNode;
  title: string;
  reducedMotion: boolean;
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const enter = reducedMotion
    ? 1
    : interpolate(frame, [0, fps * 0.6], [0, 1], {
        easing: Easing.bezier(0.16, 1, 0.3, 1),
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });

  return (
    <AbsoluteFill
      style={{
        background: colors.paper,
        color: colors.ink,
        fontFamily: "Arial, Helvetica, sans-serif",
        padding: 72,
      }}
    >
      <div
        style={{
          fontSize: 30,
          fontWeight: 700,
          letterSpacing: 3,
          textTransform: "uppercase",
          color: colors.green,
        }}
      >
        Focusly lesson
      </div>
      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          opacity: enter,
          transform: `translateY(${(1 - enter) * 32}px)`,
        }}
      >
        <h1 style={{fontSize: 70, lineHeight: 1.05, margin: "0 0 48px"}}>
          {title}
        </h1>
        {children}
      </div>
    </AbsoluteFill>
  );
};

export const LessonScene = ({
  segment,
  reducedMotion,
}: {
  segment: Segment;
  reducedMotion: boolean;
}) => {
  const layout = getSceneLayout(segment);

  switch (layout.kind) {
    case "title":
      return (
        <SceneFrame title={layout.title} reducedMotion={reducedMotion}>
          <div style={{...panel, padding: 42, fontSize: 38, color: colors.muted}}>
            {layout.eyebrow}
          </div>
        </SceneFrame>
      );
    case "bullets":
      return (
        <SceneFrame title={layout.title} reducedMotion={reducedMotion}>
          <div style={{display: "grid", gap: 22}}>
            {layout.items.map((item) => (
              <div key={item} style={{...panel, padding: "24px 32px", fontSize: 34}}>
                <span style={{color: colors.coral, marginRight: 18}}>●</span>
                {item}
              </div>
            ))}
          </div>
        </SceneFrame>
      );
    case "comparison":
      return (
        <SceneFrame title={layout.title} reducedMotion={reducedMotion}>
          <div style={{display: "grid", gridTemplateColumns: "1fr 1fr", gap: 36}}>
            {[layout.left, layout.right].map(([label, value], index) => (
              <div
                key={label}
                style={{
                  ...panel,
                  padding: 40,
                  background: index === 0 ? "#f5dcd5" : colors.mint,
                }}
              >
                <div style={{fontSize: 28, color: colors.muted}}>{label}</div>
                <div style={{fontSize: 54, fontWeight: 800, marginTop: 28}}>{value}</div>
              </div>
            ))}
          </div>
        </SceneFrame>
      );
    case "steps":
      return (
        <SceneFrame title={layout.title} reducedMotion={reducedMotion}>
          <div style={{display: "flex", alignItems: "center", gap: 20}}>
            {layout.items.map((item, index) => (
              <div key={item} style={{display: "contents"}}>
                <div style={{...panel, flex: 1, padding: 30, fontSize: 30}}>
                  <strong style={{display: "block", color: colors.coral, marginBottom: 12}}>
                    {index + 1}
                  </strong>
                  {item}
                </div>
                {index < layout.items.length - 1 ? (
                  <div style={{fontSize: 42, color: colors.green}}>→</div>
                ) : null}
              </div>
            ))}
          </div>
        </SceneFrame>
      );
    case "diagram":
      return (
        <SceneFrame title={layout.title} reducedMotion={reducedMotion}>
          <div style={{display: "flex", alignItems: "center", justifyContent: "center"}}>
            {layout.nodes.map((node, index) => (
              <div key={node} style={{display: "contents"}}>
                <div
                  style={{
                    background: index === layout.nodes.length - 1 ? colors.coral : colors.green,
                    borderRadius: 999,
                    color: colors.white,
                    fontSize: 25,
                    fontWeight: 800,
                    padding: "26px 22px",
                    textAlign: "center",
                  }}
                >
                  {node}
                </div>
                {index < layout.nodes.length - 1 ? (
                  <div style={{height: 4, width: 34, background: colors.ink}} />
                ) : null}
              </div>
            ))}
          </div>
        </SceneFrame>
      );
  }
};
