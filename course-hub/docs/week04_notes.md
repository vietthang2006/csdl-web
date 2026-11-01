# Kế hoạch thực thi truy vấn (Query Plan)

```text
QUERY PLAN
-> Sort  (cost=2914.56..2916.63 rows=828 width=39)
      Sort Key: occurred_at DESC
      Sort Method: top-N heapsort  Memory: 31kB
      Buffers: shared hit=1137
      -> Seq Scan on enrollment_events  (cost=0.00..28...
            Filter: ((occurred_at >= '2025-12-20 00:00:00'::timestamp...
            Rows Removed by Filter: 99183
            Buffers: shared hit=1137
Planning:
  Buffers: shared hit=5
Planning Time: 0.875 ms
Execution Time: 5.871 ms
```
# CourseHub - Buoi 4

- Migration 001: enrollment_events.
- Demo class: RACE-01, capacity = 1.
- POST /enrollments: lock class_sections bang FOR UPDATE.
- Concurrency test: 1 request 201, 1 request 409.
- Performance data: 100000 rows, dataset=performance.
- Index: idx_enrollment_events_dataset_student_time.
- Ghi lai scan type va Execution Time truoc/sau o day.

Khong commit backend/.env.